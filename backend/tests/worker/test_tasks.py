import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from app.db.models.document import DocumentStatus
from app.worker.tasks import run_ingestion_pipeline


@pytest.fixture
def mock_doc():
    return MagicMock(
        id=uuid.uuid4(),
        status=DocumentStatus.UPLOADED,
        storage_url="test.pdf",
        processing_metadata={},
        processing_started_at=None
    )


@pytest.mark.asyncio
async def test_run_ingestion_pipeline_success(mock_doc):
    document_id = mock_doc.id
    
    with patch("app.worker.tasks.AsyncSessionLocal") as mock_session_factory, \
         patch("app.worker.tasks.DocumentRepository") as MockRepo, \
         patch("app.worker.tasks.PDFExtractorService") as MockExtractor, \
         patch("app.worker.tasks.RecursiveTokenChunker") as MockChunker, \
         patch("app.worker.tasks.EmbeddingService") as MockEmbedding, \
         patch("app.worker.tasks.VectorDBService") as MockVDB:
        
        # Setup mocks
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        repo_instance = MockRepo.return_value
        repo_instance.get_by_id = AsyncMock(return_value=mock_doc)
        repo_instance.update = AsyncMock()
        
        extractor_instance = MockExtractor.return_value
        mock_doc_extracted = MagicMock()
        mock_doc_extracted.status = "SUCCESS"
        mock_doc_extracted.pages = [MagicMock()]
        extractor_instance.extract_text.return_value = mock_doc_extracted
        
        chunker_instance = MockChunker.return_value
        chunker_instance.chunk_document.return_value = [MagicMock()]
        
        embedding_instance = MockEmbedding.return_value
        embedding_instance.process_chunks = AsyncMock(return_value=([{"chunk": MagicMock(), "embedding": [0.1], "content_hash": "h1"}], []))
        
        vdb_instance = MockVDB.return_value
        vdb_instance.store_vectors = AsyncMock()
        
        # Run pipeline
        await run_ingestion_pipeline(document_id)
        
        # Verify stages were called
        extractor_instance.extract_text.assert_called_once()
        chunker_instance.chunk_document.assert_called_once()
        embedding_instance.process_chunks.assert_called_once()
        vdb_instance.store_vectors.assert_called_once()
        
        # Verify status updates (at least some)
        assert repo_instance.update.call_count >= 4


@pytest.mark.asyncio
async def test_run_ingestion_pipeline_failure_cleanup(mock_doc):
    document_id = mock_doc.id
    
    with patch("app.worker.tasks.AsyncSessionLocal") as mock_session_factory, \
         patch("app.worker.tasks.DocumentRepository") as MockRepo, \
         patch("app.worker.tasks.PDFExtractorService") as MockExtractor, \
         patch("app.worker.tasks.VectorDBService") as MockVDB:
        
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        repo_instance = MockRepo.return_value
        repo_instance.get_by_id = AsyncMock(return_value=mock_doc)
        repo_instance.update = AsyncMock()
        
        extractor_instance = MockExtractor.return_value
        extractor_instance.extract_text.side_effect = Exception("Extraction Failed")
        
        vdb_instance = MockVDB.return_value
        vdb_instance.delete_document_vectors = AsyncMock()
        
        # Run pipeline
        await run_ingestion_pipeline(document_id)
        
        # Verify cleanup attempt
        vdb_instance.delete_document_vectors.assert_called_once_with(document_id)
        
        # Verify status updated to FAILED
        last_update_call = repo_instance.update.call_args_list[-1]
        assert last_update_call[0][1].status == DocumentStatus.FAILED
