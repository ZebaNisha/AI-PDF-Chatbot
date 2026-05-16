import uuid
import enum
from sqlalchemy import Column, ForeignKey, String, JSON, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class MessageRole(str, enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(Base):
    """
    Stores conversational history with rich metadata for RAG observability.
    """
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    role: Mapped[MessageRole] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    
    # RAG Metadata
    citations: Mapped[list | None] = mapped_column(JSON, nullable=True) # List of dicts
    source_chunk_ids: Mapped[list | None] = mapped_column(JSON, nullable=True) # Tracking for debugging
    
    # Performance & Cost Analytics
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Prompt Tracking
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)
