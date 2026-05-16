import uuid
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from groq import RateLimitError

from app.db.models.chat import MessageRole
from app.schemas.chat import ChatStreamResponse
from app.services.chat import ChatService


@pytest.fixture
def mock_chat_repo():
    repo = AsyncMock()
    repo.get_session_history.return_value = []
    repo.create_message = AsyncMock()
    return repo


@pytest.fixture
def mock_retrieval_service():
    service = AsyncMock()
    # Mock retrieval results
    mock_response = MagicMock()
    mock_response.results = []
    service.retrieve.return_value = mock_response
    return service


@pytest.mark.asyncio
async def test_groq_chat_stream_basic(mock_chat_repo, mock_retrieval_service):
    """Test basic streaming functionality with Groq."""
    service = ChatService(
        chat_repo=mock_chat_repo, retrieval_service=mock_retrieval_service
    )

    session_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Mock Groq streaming response
    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
        MagicMock(choices=[MagicMock(delta=MagicMock(content=" Groq"))]),
    ]

    with patch("app.services.chat.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_stream

        responses = []
        async for chunk in service.stream_chat(
            query="test", user_id=user_id, session_id=session_id
        ):
            responses.append(chunk)

        assert len(responses) >= 3  # "Hello", " Groq", is_final=True
        assert any(r.delta == "Hello" for r in responses)
        assert any(r.is_final for r in responses)

        # Verify history was saved (User + Assistant)
        assert mock_chat_repo.create_message.call_count == 2


@pytest.mark.asyncio
@patch("app.services.chat.asyncio.sleep", new_callable=AsyncMock)
async def test_groq_rate_limit_retry(mock_sleep, mock_chat_repo, mock_retrieval_service):
    """Verify that Groq API rate limits trigger retries."""
    service = ChatService(
        chat_repo=mock_chat_repo, retrieval_service=mock_retrieval_service, max_retries=2
    )

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Success"))])
    ]

    with patch("app.services.chat.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        # Fail once with RateLimitError, then succeed
        mock_create.side_effect = [
            RateLimitError(
                "Rate limit", response=MagicMock(), body={"error": "too many requests"}
            ),
            mock_stream,
        ]

        responses = []
        async for chunk in service.stream_chat(
            query="test", user_id=uuid.uuid4(), session_id=uuid.uuid4()
        ):
            responses.append(chunk)

        assert mock_create.call_count == 2
        assert mock_sleep.call_count == 1
        assert any(r.delta == "Success" for r in responses)


@pytest.mark.asyncio
async def test_groq_timeout_handling(mock_chat_repo, mock_retrieval_service):
    """Verify that timeouts are handled gracefully."""
    service = ChatService(
        chat_repo=mock_chat_repo, retrieval_service=mock_retrieval_service
    )

    with patch("app.services.chat.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        # Simulate timeout
        mock_create.side_effect = asyncio.TimeoutError()

        responses = []
        async for chunk in service.stream_chat(
            query="test", user_id=uuid.uuid4(), session_id=uuid.uuid4()
        ):
            responses.append(chunk)

        assert any(r.error == "Request timed out." for r in responses)
