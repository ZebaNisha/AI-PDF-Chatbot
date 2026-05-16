from typing import Any
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.api.dependencies.auth import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.repositories.chat import ChatRepository
from app.services.vector_search import VectorSearchService
from app.services.embedding import EmbeddingService
from app.services.chat import ChatService
from app.services.retrieval import RetrievalService
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/stream")
async def stream_chat_response(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Stream AI chat response using Server-Sent Events (SSE).
    """
    chat_repo = ChatRepository(db)
    vector_service = VectorSearchService()
    embedding_service = EmbeddingService()
    retrieval_service = RetrievalService(embedding_service, vector_service)
    chat_service = ChatService(chat_repo, retrieval_service)

    async def event_generator():
        try:
            async for chunk in chat_service.stream_chat(
                query=request.query,
                user_id=current_user.id,
                session_id=request.session_id,
                document_ids=request.document_ids,
            ):
                yield {
                    "event": "message",
                    "data": chunk.model_dump_json(),
                }
        except Exception as e:
            yield {
                "event": "error",
                "data": str(e),
            }

    return EventSourceResponse(event_generator())


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve chat history for a specific session.
    """
    chat_repo = ChatRepository(db)
    history = await chat_repo.get_session_history(session_id=session_id, limit=limit)
    return history
