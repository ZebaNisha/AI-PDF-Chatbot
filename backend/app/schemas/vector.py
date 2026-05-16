import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class VectorMetadata(BaseModel):
    """
    Schema for the optimized payload stored alongside vectors in Qdrant.
    Contains essential metadata for retrieval filtering and tracing.
    """
    chunk_id: str = Field(..., description="UUID of the chunk")
    document_id: str = Field(..., description="UUID of the parent document")
    user_id: str = Field(..., description="UUID of the owner user")
    text: str = Field(..., description="The chunk text")
    start_page: int = Field(..., description="Starting page of the chunk")
    end_page: int = Field(..., description="Ending page of the chunk")
    chunk_index: int = Field(..., description="0-based index of the chunk")
    
    # Traceability and caching
    model_name: str = Field(..., description="Embedding model used")
    embedding_dimension: int = Field(..., description="Dimension of the vector")
    provider: str = Field(default="sentence-transformers", description="Provider of the embeddings")
    created_at: str = Field(..., description="ISO timestamp of embedding creation")
    content_hash: str = Field(..., description="SHA-256 hash of the text content")
    embedding_version: str = Field(..., description="Version of the chunking/embedding pipeline")
    token_count: int = Field(..., description="Number of tokens in the chunk")
