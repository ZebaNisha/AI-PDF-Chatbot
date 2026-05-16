import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models.document import DocumentStatus


class DocumentBase(BaseModel):
    original_filename: str
    file_size: int
    mime_type: str


class DocumentCreate(DocumentBase):
    user_id: uuid.UUID
    stored_filename: str
    storage_url: str | None = None
    status: DocumentStatus = DocumentStatus.PENDING


class DocumentUpdate(BaseModel):
    status: DocumentStatus | None = None
    storage_url: str | None = None


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    stored_filename: str
    storage_url: str | None
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
