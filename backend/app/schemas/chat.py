import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

from app.db.models.chat import MessageRole
from app.schemas.retrieval import Citation


class ChatMessageBase(BaseModel):
    role: MessageRole
    content: str


class ChatMessageCreate(ChatMessageBase):
    session_id: uuid.UUID
    user_id: uuid.UUID
    citations: Optional[List[Dict[str, Any]]] = None
    source_chunk_ids: Optional[List[str]] = None
    model_name: Optional[str] = None
    token_count: Optional[int] = None
    latency_ms: Optional[float] = None
    prompt_version: Optional[str] = None


class ChatMessageResponse(ChatMessageBase):
    id: uuid.UUID
    created_at: datetime
    citations: Optional[List[Citation]] = None
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's question")
    session_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, description="Unique ID for the chat session")
    document_ids: Optional[List[uuid.UUID]] = Field(None, description="Specific documents to target")
    stream: bool = Field(True, description="Whether to stream the response")


class ChatStreamResponse(BaseModel):
    """
    Schema for individual chunks in the streaming response.
    """
    delta: Optional[str] = None
    is_final: bool = False
    citations: Optional[List[Citation]] = None
    error: Optional[str] = None
