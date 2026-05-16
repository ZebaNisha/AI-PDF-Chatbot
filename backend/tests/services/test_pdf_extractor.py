import fitz
import pytest

from app.schemas.pdf import ExtractionStatus
from app.services.pdf_extractor import PDFExtractorService
from app.utils.text_cleaner import clean_extracted_text


def create_mock_pdf_bytes() -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "Hello   World!\n\n\nThis is a test.")

    # Add metadata
    doc.set_metadata({"title": "Test PDF", "author": "Tester"})

    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_clean_extracted_text():
    raw_text = "Hello \x00 World!   \n\n\n\nTesting."
    cleaned = clean_extracted_text(raw_text)
    assert cleaned == "Hello World! \n\nTesting."


def test_pdf_extractor_success():
    pdf_bytes = create_mock_pdf_bytes()

    result = PDFExtractorService.extract_text(pdf_bytes)

    assert result.status == ExtractionStatus.SUCCESS
    assert result.total_pages == 1
    assert len(result.pages) == 1

    page = result.pages[0]
    assert page.page_number == 1
    assert "Hello World!" in page.text
    assert page.char_count == len(page.text)
    assert page.error is None

    assert result.metadata["title"] == "Test PDF"
    assert result.metadata["author"] == "Tester"


def test_pdf_extractor_failure():
    # Provide invalid bytes
    result = PDFExtractorService.extract_text(b"not a pdf")

    assert result.status == ExtractionStatus.FAILED
    assert result.total_pages == 0
    assert "Failed to open PDF" in result.error
