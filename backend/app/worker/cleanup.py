import asyncio
import uuid
from app.worker.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.repositories.document import DocumentRepository
from app.services.vector_db import VectorDBService
import structlog

logger = structlog.get_logger(__name__)

async def run_vector_cleanup(document_id: uuid.UUID):
    """
    Asynchronously remove vectors and metadata for a deleted document.
    """
    async with AsyncSessionLocal() as session:
        doc_repo = DocumentRepository(session)
        # We don't need the doc to exist, just the ID to filter in Qdrant
        vector_db_service = VectorDBService(doc_repo)
        await vector_db_service.delete_document_vectors(document_id)
        logger.info("async_vector_cleanup_complete", document_id=str(document_id))

@celery_app.task(name="cleanup_document_vectors")
def cleanup_document_vectors_task(document_id_str: str):
    """
    Celery task wrapper for vector cleanup.
    """
    logger.info("cleanup_task_started", document_id=document_id_str)
    try:
        asyncio.run(run_vector_cleanup(uuid.UUID(document_id_str)))
    except Exception as e:
        logger.error("cleanup_task_failed", document_id=document_id_str, error=str(e))
        raise
