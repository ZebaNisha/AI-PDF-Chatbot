import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.chunk import DocumentChunk
from app.services.vector_db import VectorDBService


@pytest.fixture
def mock_document_repo():
    repo = AsyncMock()
    repo.get_by_id.return_value = AsyncMock()  # Return a mock document
    return repo


@pytest.fixture
def mock_successful_embeddings():
    chunk = DocumentChunk(
        document_id=uuid.uuid4(),
        chunk_index=0,
        text="Sample text",
        start_page=1,
        end_page=1,
        start_char=0,
        end_char=10,
        token_count=3,
        character_count=10,
    )
    return [
        {
            "chunk": chunk,
            "embedding": [0.1] * 1536,
            "content_hash": "testhash",
        }
    ]


@pytest.mark.asyncio
async def test_store_vectors_success(mock_document_repo, mock_successful_embeddings):
    service = VectorDBService(document_repo=mock_document_repo)

    with patch("app.services.vector_db.qdrant_client.upsert", new_callable=AsyncMock) as mock_upsert:
        doc_id = mock_successful_embeddings[0]["chunk"].document_id
        await service.store_vectors(doc_id, mock_successful_embeddings)

        mock_upsert.assert_called_once()
        mock_document_repo.update.assert_called_once()
        # Ensure status is updated to COMPLETED
        update_call_args = mock_document_repo.update.call_args[0]
        assert update_call_args[1].status.value == "COMPLETED"


@pytest.mark.asyncio
async def test_store_vectors_failure(mock_document_repo, mock_successful_embeddings):
    service = VectorDBService(document_repo=mock_document_repo)

    with patch("app.services.vector_db.qdrant_client.upsert", new_callable=AsyncMock) as mock_upsert:
        mock_upsert.side_effect = Exception("Qdrant down")

        doc_id = mock_successful_embeddings[0]["chunk"].document_id

        with pytest.raises(Exception):
            await service.store_vectors(doc_id, mock_successful_embeddings)

        mock_document_repo.update.assert_called_once()
        # Ensure status is updated to FAILED
        update_call_args = mock_document_repo.update.call_args[0]
        assert update_call_args[1].status.value == "FAILED"


@pytest.mark.asyncio
async def test_delete_vectors(mock_document_repo):
    service = VectorDBService(document_repo=mock_document_repo)

    with patch("app.services.vector_db.qdrant_client.delete", new_callable=AsyncMock) as mock_delete:
        doc_id = uuid.uuid4()
        await service.delete_document_vectors(doc_id)

        mock_delete.assert_called_once()
