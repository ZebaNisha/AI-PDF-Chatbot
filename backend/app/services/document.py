import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.db.models.document import Document, DocumentStatus
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentCreate

settings = get_settings()

UPLOAD_DIR = Path("uploads")
# Ensure the upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class DocumentService:
    def __init__(self, document_repo: DocumentRepository):
        self.document_repo = document_repo

    async def upload_document(self, file: UploadFile, user_id: uuid.UUID) -> Document:
        # 1. Validate MIME type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed.",
            )

        # 2. Validate file size
        # Read the whole file to check size (for files larger than memory, they are spooled to disk by FastAPI)
        # However, to check size before saving, we can seek to end or check file.size in newer FastAPI versions.
        # file.size is available in FastAPI >= 0.100.0
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file.size and file.size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File is too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB.",
            )

        # Generate a unique stored filename
        stored_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = UPLOAD_DIR / stored_filename

        # 3. Save the file locally
        try:
            with open(file_path, "wb") as buffer:
                # Read chunks to avoid loading large files into memory
                while content := await file.read(1024 * 1024):  # 1MB chunks
                    buffer.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not save file: {str(e)}"
            )

        # Provide a fallback for file.size if it wasn't available
        file_size = file.size if file.size is not None else os.path.getsize(file_path)

        # Check size again if fallback was used
        if file_size > max_size_bytes:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File is too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB.",
            )

        # 4. Save metadata to database
        doc_in = DocumentCreate(
            user_id=user_id,
            original_filename=file.filename or "unknown.pdf",
            stored_filename=stored_filename,
            storage_url=str(file_path),
            file_size=file_size,
            mime_type=file.content_type,
            status=DocumentStatus.PENDING,
        )

        document = await self.document_repo.create(doc_in)
        return document
