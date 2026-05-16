import fitz  # PyMuPDF

from app.schemas.pdf import ExtractedDocument, ExtractedPage, ExtractionStatus
from app.utils.text_cleaner import clean_extracted_text


class PDFExtractorService:
    @staticmethod
    def extract_text(file_path_or_bytes: str | bytes) -> ExtractedDocument:
        """
        Extracts and cleans text from a PDF document page-by-page.
        Handles status reporting and individual page errors.
        """
        try:
            if isinstance(file_path_or_bytes, bytes):
                doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")
            else:
                doc = fitz.open(file_path_or_bytes)
        except Exception as e:
            return ExtractedDocument(
                total_pages=0,
                status=ExtractionStatus.FAILED,
                error=f"Failed to open PDF: {str(e)}",
            )

        extracted_pages = []
        status = ExtractionStatus.SUCCESS

        metadata = {
            "title": doc.metadata.get("title"),
            "author": doc.metadata.get("author"),
            "subject": doc.metadata.get("subject"),
            "creator": doc.metadata.get("creator"),
        }

        total_pages = len(doc)

        for page_num in range(total_pages):
            try:
                page = doc.load_page(page_num)
                raw_text = page.get_text("text")
                cleaned_text = clean_extracted_text(raw_text)

                extracted_pages.append(
                    ExtractedPage(
                        page_number=page_num + 1,
                        text=cleaned_text,
                        char_count=len(cleaned_text),
                    )
                )
            except Exception as e:
                status = ExtractionStatus.PARTIAL
                extracted_pages.append(
                    ExtractedPage(
                        page_number=page_num + 1,
                        text="",
                        char_count=0,
                        error=f"Failed to extract page: {str(e)}",
                    )
                )

        doc.close()

        return ExtractedDocument(
            pages=extracted_pages,
            total_pages=total_pages,
            status=status,
            metadata=metadata,
        )
