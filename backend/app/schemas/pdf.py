import enum

from pydantic import BaseModel, Field


class ExtractionStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class ExtractedPage(BaseModel):
    page_number: int = Field(..., description="1-indexed page number")
    text: str = Field(..., description="Cleaned extracted text from the page")
    char_count: int = Field(..., description="Number of characters in the cleaned text")
    error: str | None = Field(None, description="Error message if extraction failed for this page")


class ExtractedDocument(BaseModel):
    pages: list[ExtractedPage] = Field(default_factory=list)
    total_pages: int = Field(..., description="Total number of pages in the document")
    status: ExtractionStatus = Field(..., description="Overall extraction status")
    error: str | None = Field(None, description="Global error message if extraction failed")
    metadata: dict[str, str | None] = Field(default_factory=dict, description="Document metadata (author, title, etc)")
