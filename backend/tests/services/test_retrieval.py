import uuid
from unittest.mock import AsyncMock, patch
import pytest

from app.schemas.retrieval import RetrievalResponse
from app.services.retrieval import RetrievalService


@pytest.fixture
def mock_embedding_service():
    service = AsyncMock()
    # Mock single embedding return (a vector of 1536 floats)
    service._embed_batch_with_retry.return_value = [[0.1] * 1536]
    return service


@pytest.fixture
def mock_vector_search_service():
    service = AsyncMock()
    return service


@pytest.fixture
def sample_payload():
    return {
        "text": "This is a test chunk.",
        "document_id": str(uuid.uuid4()),
        "chunk_id": str(uuid.uuid4()),
        "start_page": 1,
        "end_page": 1,
        "chunk_index": 0,
        "token_count": 10,
        "content_hash": "hash1"
    }


@pytest.mark.asyncio
async def test_retrieval_success(mock_embedding_service, mock_vector_search_service, sample_payload):
    service = RetrievalService(
        embedding_service=mock_embedding_service,
        vector_search_service=mock_vector_search_service
    )
    
    # Mock Qdrant results
    mock_hit = AsyncMock()
    mock_hit.score = 0.9
    mock_hit.payload = sample_payload
    mock_vector_search_service.search_vectors.return_value = [mock_hit]
    
    user_id = uuid.uuid4()
    response = await service.retrieve(query="What is testing?", user_id=user_id)
    
    assert isinstance(response, RetrievalResponse)
    assert len(response.results) == 1
    assert response.results[0].text == "This is a test chunk."
    assert response.metrics.total_latency_ms > 0
    assert response.results[0].citation.document_id == uuid.UUID(sample_payload["document_id"])


@pytest.mark.asyncio
async def test_retrieval_deduplication(mock_embedding_service, mock_vector_search_service, sample_payload):
    service = RetrievalService(
        embedding_service=mock_embedding_service,
        vector_search_service=mock_vector_search_service
    )
    
    # Create two identical hits
    mock_hit = AsyncMock()
    mock_hit.score = 0.9
    mock_hit.payload = sample_payload
    
    mock_vector_search_service.search_vectors.return_value = [mock_hit, mock_hit]
    
    response = await service.retrieve(query="test", user_id=uuid.uuid4())
    
    # Should only return one result due to deduplication
    assert len(response.results) == 1


@pytest.mark.asyncio
async def test_retrieval_diversity(mock_embedding_service, mock_vector_search_service, sample_payload):
    # Set diversity limits low for testing
    with patch("app.services.retrieval.settings.RETRIEVAL_MAX_CHUNKS_PER_DOC", 1):
        service = RetrievalService(
            embedding_service=mock_embedding_service,
            vector_search_service=mock_vector_search_service
        )
        
        # Two hits from the same document
        hit1 = AsyncMock(score=0.9, payload=sample_payload)
        hit2 = AsyncMock(score=0.8, payload={**sample_payload, "chunk_id": str(uuid.uuid4()), "chunk_index": 1})
        
        mock_vector_search_service.search_vectors.return_value = [hit1, hit2]
        
        response = await service.retrieve(query="test", user_id=uuid.uuid4())
        
        # Should only return one result due to diversity limit (1 per doc)
        assert len(response.results) == 1


@pytest.mark.asyncio
async def test_retrieval_empty_results(mock_embedding_service, mock_vector_search_service):
    service = RetrievalService(
        embedding_service=mock_embedding_service,
        vector_search_service=mock_vector_search_service
    )
    
    mock_vector_search_service.search_vectors.return_value = []
    
    response = await service.retrieve(query="nothing", user_id=uuid.uuid4())
    
    assert len(response.results) == 0
    assert response.total_results == 0
