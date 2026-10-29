"""Lightweight, local RAG retrieval with source-level citations.

PDF uploads are held in process memory only. Retrieval is lexical (not embedding-based)
so the demo remains deterministic and does not need an external vector database.
"""
from collections import Counter
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re
from threading import RLock
from typing import Any

from pypdf import PdfReader

ROOT_DIR = Path(__file__).resolve().parent.parent
POLICIES_DIR = ROOT_DIR / "policies"
MAX_QUERY_LENGTH = 300
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 100
MAX_EXTRACTED_CHARS = 1_000_000
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
MAX_RESULTS = 5

_TOKEN_RE = re.compile(r"[\w\u0600-\u06ff]+", re.UNICODE)
_uploaded_documents: dict[str, list[dict[str, Any]]] = {}
_uploaded_lock = RLock()


def _tokens(text: str) -> list[str]:
    return [token.casefold() for token in _TOKEN_RE.findall(text) if len(token) > 1]


def _split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    chunks = []
    start = 0
    while start < len(cleaned):
        end = min(start + size, len(cleaned))
        if end < len(cleaned):
            boundary = cleaned.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _chunk_record(source: str, text: str, page: int | None = None) -> list[dict[str, Any]]:
    records = []
    for index, chunk in enumerate(_split_text(text), start=1):
        records.append({
            "source": source,
            "page": page,
            "chunk": index,
            "content": chunk,
            "citation": f"[{source}, page {page}]" if page is not None else f"[{source}, chunk {index}]",
            "synthetic": page is None,
        })
    return records


def _local_chunks() -> list[dict[str, Any]]:
    records = []
    if not POLICIES_DIR.exists():
        return records
    for path in sorted(POLICIES_DIR.glob("*.md")):
        try:
            records.extend(_chunk_record(path.name, path.read_text(encoding="utf-8")))
        except OSError:
            continue
    return records


def add_pdf_document(filename: str, content: bytes) -> dict[str, Any]:
    """Extract a PDF into bounded, in-memory page chunks."""
    if not isinstance(filename, str) or not filename.strip():
        return {"ok": False, "error": "A filename is required."}
    if not isinstance(content, bytes) or not content:
        return {"ok": False, "error": "The PDF is empty."}
    if len(content) > MAX_UPLOAD_BYTES:
        return {"ok": False, "error": "PDF exceeds the 5 MB upload limit."}
    if not content.startswith(b"%PDF-"):
        return {"ok": False, "error": "The uploaded file is not a valid PDF."}

    safe_name = Path(filename.replace("\\", "/")).name.strip()
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
    try:
        reader = PdfReader(BytesIO(content), strict=True)
        if reader.is_encrypted:
            return {"ok": False, "error": "Encrypted PDFs are not supported."}
        if len(reader.pages) == 0 or len(reader.pages) > MAX_PDF_PAGES:
            return {"ok": False, "error": "PDF must contain between 1 and 100 pages."}
        pages = []
        total_chars = 0
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            total_chars += len(text)
            if total_chars > MAX_EXTRACTED_CHARS:
                return {"ok": False, "error": "Extracted PDF text exceeds the 1 MB limit."}
            if text.strip():
                pages.extend(_chunk_record(safe_name, text, page=page_number))
        if not pages:
            return {"ok": False, "error": "No extractable text was found. Scanned PDFs need OCR, which is not enabled."}
    except Exception:
        return {"ok": False, "error": "Could not read this PDF. Try a valid, text-based PDF."}

    with _uploaded_lock:
        _uploaded_documents[safe_name] = pages
    return {"ok": True, "source": safe_name, "pages": len(reader.pages), "chunks": len(pages)}


def list_uploaded_documents() -> list[dict[str, Any]]:
    with _uploaded_lock:
        return [{"source": name, "chunks": len(chunks)} for name, chunks in sorted(_uploaded_documents.items())]


def clear_uploaded_documents() -> None:
    """Clear in-memory PDF content; intended for tests and local demos."""
    with _uploaded_lock:
        _uploaded_documents.clear()


def retrieve_chunks(query: str, top_k: int = MAX_RESULTS) -> dict[str, Any]:
    if not isinstance(query, str) or not query.strip():
        return {"ok": False, "error": "Search query cannot be empty.", "results": []}
    if len(query) > MAX_QUERY_LENGTH:
        return {"ok": False, "error": "Search query is too long.", "results": []}
    query_tokens = _tokens(query)
    if not query_tokens:
        return {"ok": True, "query": query, "results": [], "retrieval": "lexical", "synthetic": True}

    chunks = _local_chunks()
    with _uploaded_lock:
        for document_chunks in _uploaded_documents.values():
            chunks.extend(document_chunks)

    query_counts = Counter(query_tokens)
    query_set = set(query_tokens)
    ranked = []
    query_phrase = " ".join(query_tokens)
    for chunk in chunks:
        chunk_tokens = _tokens(chunk["content"])
        if not chunk_tokens:
            continue
        counts = Counter(chunk_tokens)
        overlap = sum(min(counts[token], query_counts[token]) for token in query_set)
        if overlap == 0:
            continue
        # Normalized term coverage plus a small phrase match bonus.
        score = overlap / max(len(query_set), 1)
        normalized_content = " ".join(chunk_tokens)
        if query_phrase and query_phrase in normalized_content:
            score += 0.25
        ranked.append({**chunk, "score": round(score, 4), "retrieval": "lexical"})
    ranked.sort(key=lambda item: (-item["score"], item["source"], item["page"] or 0, item["chunk"]))
    try:
        limit = max(1, min(int(top_k), MAX_RESULTS))
    except (TypeError, ValueError):
        limit = MAX_RESULTS
    return {
        "ok": True,
        "query": query,
        "results": ranked[:limit],
        "retrieval": "lexical",
        "synthetic": all(item["synthetic"] for item in ranked[:limit]),
    }
