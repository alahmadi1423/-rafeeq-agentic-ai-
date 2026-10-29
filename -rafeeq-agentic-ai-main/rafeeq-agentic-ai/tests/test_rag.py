from io import BytesIO

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.rag import add_pdf_document, clear_uploaded_documents, retrieve_chunks


def test_retrieval_returns_source_citations_for_local_policy():
    result = retrieve_chunks("food truck application requirements")

    assert result["ok"] is True
    assert result["results"]
    assert result["results"][0]["source"] == "food_truck_policy.md"
    assert result["results"][0]["citation"].startswith("[food_truck_policy.md, chunk ")
    assert result["results"][0]["content"]


def test_retrieval_rejects_empty_and_oversized_queries():
    assert retrieve_chunks("  ")["ok"] is False
    assert retrieve_chunks("x" * 301)["ok"] is False


def test_pdf_upload_rejects_non_pdf_bytes():
    result = add_pdf_document("policy.pdf", b"not a pdf")
    assert result["ok"] is False


def _text_pdf(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    font_ref = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref})
    })
    stream = DecodedStreamObject()
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream.set_data(f"BT /F1 12 Tf 10 100 Td ({escaped}) Tj ET".encode("latin-1"))
    page[NameObject("/Contents")] = writer._add_object(stream)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_pdf_upload_extracts_text_and_query_returns_page_citation():
    clear_uploaded_documents()
    result = add_pdf_document("permit-guide.pdf", _text_pdf("Food truck permit application requirements"))
    assert result["ok"] is True
    assert result["pages"] == 1
    assert result["chunks"] == 1

    search = retrieve_chunks("food truck permit requirements")
    assert search["ok"] is True
    assert search["results"]
    assert search["results"][0]["source"] == "permit-guide.pdf"
    assert search["results"][0]["citation"] == "[permit-guide.pdf, page 1]"
    assert "application requirements" in search["results"][0]["content"].lower()
    assert search["results"][0]["synthetic"] is False
    clear_uploaded_documents()


def test_uploaded_filename_is_sanitized_and_listed():
    clear_uploaded_documents()
    result = add_pdf_document("../../demo.pdf", _text_pdf("Food truck permit requirements"))
    assert result["ok"] is True
    assert result["source"] == "demo.pdf"
    from app.rag import list_uploaded_documents
    assert list_uploaded_documents()[0]["source"] == "demo.pdf"
    clear_uploaded_documents()
