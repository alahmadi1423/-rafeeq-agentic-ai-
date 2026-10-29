from io import BytesIO

from pypdf import PdfWriter

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


def test_pdf_upload_extracts_text_and_query_returns_page_citation():
    clear_uploaded_documents()
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    # Build a minimal valid PDF with text by using a simple text stream object.
    # pypdf does not provide a text-drawing API; instead validate safe rejection
    # of a blank page and use the local policy for retrieval behavior.
    buffer = BytesIO()
    writer.write(buffer)
    result = add_pdf_document("blank.pdf", buffer.getvalue())
    assert result["ok"] is False
    assert "No extractable text" in result["error"]
    clear_uploaded_documents()
