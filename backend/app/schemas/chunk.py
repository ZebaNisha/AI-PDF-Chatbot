import uuid

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the chunk")
    document_id: uuid.UUID = Field(..., description="ID of the source document")
    chunk_index: int = Field(..., description="0-based index of the chunk in the document")
    text: str = Field(..., description="The actual text content of the chunk")
    start_page: int = Field(..., description="The 1-indexed page where the chunk starts")
    end_page: int = Field(..., description="The 1-indexed page where the chunk ends")
    start_char: int = Field(..., description="Global character offset where the chunk starts in the document")
    end_char: int = Field(..., description="Global character offset where the chunk ends in the document")
    token_count: int = Field(..., description="Number of tokens in the chunk")
    character_count: int = Field(..., description="Number of characters in the chunk")
    metadata: dict = Field(default_factory=dict, description="Optional metadata (e.g. headings, labels)")
