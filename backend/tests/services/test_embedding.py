import uuid
from unittest.mock import MagicMock, patch

import pytest
import torch
from app.schemas.chunk import DocumentChunk
from app.services.embedding import EmbeddingService


@pytest.fixture
def mock_chunks():
    return [
        DocumentChunk(
            document_id=uuid.uuid4(),
            chunk_index=i,
            text=f"Sample text {i}",
            start_page=1,
            end_page=1,
            start_char=0,
            end_char=10,
            token_count=3,
            character_count=10,
        )
        for i in range(5)
    ]


@pytest.mark.asyncio
async def test_embedding_singleton():
    """Verify that EmbeddingService is a singleton."""
    service1 = EmbeddingService()
    service2 = EmbeddingService()
    assert service1 is service2


@pytest.mark.asyncio
async def test_process_chunks_local(mock_chunks):
    """Test chunk processing using a mocked local model."""
    service = EmbeddingService()

    # Mock the internal model and its encode method
    mock_model = MagicMock()
    # Return 384-dimension vectors
    mock_model.encode.return_value = torch.ones((len(mock_chunks), 384)).numpy()

    with patch.object(EmbeddingService, "_model", mock_model):
        successful, failed = await service.process_chunks(mock_chunks)

        assert len(successful) == 5
        assert len(failed) == 0
        assert len(successful[0]["embedding"]) == 384
        assert successful[0]["content_hash"] is not None
        assert mock_model.encode.called


@pytest.mark.asyncio
async def test_process_chunks_with_empty_text(mock_chunks):
    """Verify that empty chunks are handled gracefully."""
    service = EmbeddingService()
    mock_chunks[0].text = "   "  # Empty whitespace

    mock_model = MagicMock()
    mock_model.encode.return_value = torch.ones((len(mock_chunks) - 1, 384)).numpy()

    with patch.object(EmbeddingService, "_model", mock_model):
        successful, failed = await service.process_chunks(mock_chunks)

        assert len(successful) == 4
        assert len(failed) == 1
        assert mock_chunks[0] in failed


@pytest.mark.asyncio
async def test_embedding_cache(mock_chunks):
    """Verify that embeddings are cached and not re-generated."""
    service = EmbeddingService()
    service.cache = {}  # Clear cache for test isolation

    mock_model = MagicMock()
    mock_model.encode.return_value = torch.ones((len(mock_chunks), 384)).numpy()

    with patch.object(EmbeddingService, "_model", mock_model):
        # First call - embeds everything
        await service.process_chunks(mock_chunks)
        assert mock_model.encode.call_count == 1

        # Second call - everything should be in cache
        successful, failed = await service.process_chunks(mock_chunks)
        assert len(successful) == 5
        assert len(failed) == 0
        # encode should NOT have been called again
        assert mock_model.encode.call_count == 1
