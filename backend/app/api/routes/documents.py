import uuid
from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF document.
    """
    document_repo = DocumentRepository(db)
    document_service = DocumentService(document_repo)
    
    document = await document_service.upload_document(file, current_user.id)
    
    # Trigger background processing
    from app.worker.tasks import process_document_task
    process_document_task.delay(str(document.id))
    
    return document
@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all documents for the current user.
    """
    document_repo = DocumentRepository(db)
    return await document_repo.get_multi_by_user(user_id=current_user.id)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get document by ID.
    """
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document.
    """
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await document_repo.delete(document_id)
    return None
