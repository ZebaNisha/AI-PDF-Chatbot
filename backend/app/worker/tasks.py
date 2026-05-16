import asyncio
import uuid
import traceback
from datetime import datetime, timezone
from celery import Task

import app.db.base  # Ensure all models are registered with SQLAlchemy
import structlog
from app.worker.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.db.models.document import DocumentStatus
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentUpdate
from app.schemas.pdf import ExtractionStatus
from app.services.pdf_extractor import PDFExtractorService
from app.services.chunker import RecursiveTokenChunker
from app.services.embedding import EmbeddingService
from app.services.vector_db import VectorDBService

logger = structlog.get_logger(__name__)


async def update_doc_status(
    doc_repo: DocumentRepository,
    doc_id: uuid.UUID,
    status: DocumentStatus,
    failure_reason: str = None,
    metadata: dict = None,
):
    """
    Helper to update document status and metadata during processing.
    """
    doc = await doc_repo.get_by_id(doc_id)
    if not doc:
        return

    update_data = {"status": status}
    if failure_reason:
        update_data["failure_reason"] = failure_reason
    if metadata:
        current_meta = doc.processing_metadata or {}
        update_data["processing_metadata"] = {**current_meta, **metadata}
    
    if status == DocumentStatus.COMPLETED:
        update_data["processing_completed_at"] = datetime.now(timezone.utc)
    elif status == DocumentStatus.EXTRACTING and not doc.processing_started_at:
        update_data["processing_started_at"] = datetime.now(timezone.utc)

    await doc_repo.update(doc, DocumentUpdate(**update_data))


async def run_ingestion_pipeline(document_id: uuid.UUID):
    """
    The core modular RAG ingestion pipeline.
    """
    async with AsyncSessionLocal() as session:
        doc_repo = DocumentRepository(session)
        doc = await doc_repo.get_by_id(document_id)

        if not doc:
            logger.error("pipeline_aborted_document_not_found", document_id=str(document_id))
            return

        # Idempotency check: Don't process if already completed or currently processing
        if doc.status in [DocumentStatus.COMPLETED, DocumentStatus.EXTRACTING, DocumentStatus.CHUNKING, DocumentStatus.EMBEDDING, DocumentStatus.STORING]:
            logger.info("pipeline_skipped_idempotency", document_id=str(document_id), current_status=doc.status)
            return

        try:
            # --- STAGE 1: EXTRACTION ---
            await update_doc_status(doc_repo, document_id, DocumentStatus.EXTRACTING)
            extractor = PDFExtractorService()
            # Note: doc.storage_url would be the local path in this initial dev phase
            extracted_doc = await asyncio.to_thread(extractor.extract_text, doc.storage_url)
            
            if extracted_doc.status == ExtractionStatus.FAILED:
                raise Exception(f"PDF extraction failed: {extracted_doc.error}")
                
            page_count = len(extracted_doc.pages)
            logger.info("stage_extraction_complete", document_id=str(document_id), page_count=page_count)

            # --- STAGE 2: CHUNKING ---
            await update_doc_status(doc_repo, document_id, DocumentStatus.CHUNKING, metadata={"pages_extracted": page_count})
            chunker = RecursiveTokenChunker()
            chunks = chunker.chunk_document(document_id, extracted_doc)
            logger.info("stage_chunking_complete", document_id=str(document_id), chunk_count=len(chunks))

            # --- STAGE 3: EMBEDDING ---
            await update_doc_status(doc_repo, document_id, DocumentStatus.EMBEDDING, metadata={"chunk_count": len(chunks)})
            embedding_service = EmbeddingService()
            successful_embeddings, failed_chunks = await embedding_service.process_chunks(chunks)
            
            if failed_chunks:
                logger.warning("partial_embedding_failure", document_id=str(document_id), failed_count=len(failed_chunks))

            # --- STAGE 4: STORAGE ---
            await update_doc_status(doc_repo, document_id, DocumentStatus.STORING, metadata={"embeddings_generated": len(successful_embeddings)})
            vector_db_service = VectorDBService(doc_repo)
            await vector_db_service.store_vectors(document_id, successful_embeddings)
            
            # VectorDBService.store_vectors already updates status to COMPLETED on success
            logger.info("pipeline_completed_successfully", document_id=str(document_id))

        except Exception as e:
            error_msg = f"Error in pipeline: {str(e)}\n{traceback.format_exc()}"
            logger.error("pipeline_failed", document_id=str(document_id), error=error_msg)
            
            # Rollback the transaction in case the exception was a DB error, 
            # so we can use the session to update the status
            await session.rollback()
            
            await update_doc_status(doc_repo, document_id, DocumentStatus.FAILED, failure_reason=str(e))
            
            # Partial Cleanup on Failure (Optional but requested)
            # If we reached storage and failed, we might want to attempt deleting vectors for this doc_id
            try:
                # We need to re-init VectorDBService since it's scoped to the session
                vdb = VectorDBService(doc_repo)
                await vdb.delete_document_vectors(document_id)
                logger.info("partial_cleanup_complete", document_id=str(document_id))
            except Exception as cleanup_err:
                logger.error("cleanup_failed", document_id=str(document_id), error=str(cleanup_err))


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id_str: str):
    """
    Celery task wrapper for the async ingestion pipeline.
    """
    logger.info("celery_task_started", task_id=self.request.id, document_id=document_id_str)
    try:
        # Reuse a single event loop per worker process to prevent asyncpg connection pool breakage
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.run_until_complete(run_ingestion_pipeline(uuid.UUID(document_id_str)))
        # Do NOT close the loop here, so the global SQLAlchemy engine can reuse it!
    except Exception as exc:
        logger.error("celery_task_fatal_error", task_id=self.request.id, error=str(exc))
        raise self.retry(exc=exc, countdown=60)
