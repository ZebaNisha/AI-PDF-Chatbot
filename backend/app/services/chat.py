import uuid
import time
import asyncio
import random
from typing import AsyncGenerator, List, Optional, Dict, Any

import structlog
from groq import AsyncGroq, RateLimitError, APIStatusError
from app.core.config import get_settings
from app.db.models.chat import MessageRole
from app.repositories.chat import ChatRepository
from app.schemas.chat import ChatMessageCreate, ChatStreamResponse
from app.services.retrieval import RetrievalService
from app.services.prompts import PromptService
from app.utils.token_counter import count_tokens

logger = structlog.get_logger(__name__)
settings = get_settings()

# Initialize Groq client
client = AsyncGroq(api_key=settings.GROQ_API_KEY)


class ChatService:
    """
    Orchestrates the conversational RAG flow using Groq.
    Includes memory retrieval, context injection, generation with retries, and persistence.
    """

    def __init__(
        self,
        chat_repo: ChatRepository,
        retrieval_service: RetrievalService,
        max_retries: int = 3,
    ):
        self.chat_repo = chat_repo
        self.retrieval_service = retrieval_service
        self.max_retries = max_retries

    async def stream_chat(
        self,
        query: str,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
    ) -> AsyncGenerator[ChatStreamResponse, None]:
        """
        Main RAG chat entry point with streaming and context management using Groq.
        """
        start_time = time.perf_counter()

        # 1. Retrieve Context
        retrieval_response = await self.retrieval_service.retrieve(
            query=query,
            user_id=user_id,
            document_ids=document_ids,
            top_k=settings.CHAT_MAX_RETRIEVED_CHUNKS,
            debug=False,
        )

        # 2. Get Session History
        history = await self.chat_repo.get_session_history(
            session_id=session_id, limit=settings.CHAT_MEMORY_WINDOW
        )

        # 3. Build Prompt
        context_text = PromptService.build_context_text(retrieval_response.results)
        messages = PromptService.build_final_messages(query, context_text, history)

        # 4. Save User Message
        await self.chat_repo.create_message(
            ChatMessageCreate(
                session_id=session_id,
                user_id=user_id,
                role=MessageRole.USER,
                content=query,
            )
        )

        full_response_content = ""
        citations = [res.citation for res in retrieval_response.results]
        source_chunk_ids = [
            str(res.citation.chunk_id) for res in retrieval_response.results
        ]

        # 5. Call Groq LLM with Streaming and Retries
        attempt = 0
        stream_started = False
        while attempt < self.max_retries:
            try:
                stream = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=settings.GROQ_CHAT_MODEL,
                        messages=messages,
                        stream=True,
                    ),
                    timeout=settings.CHAT_TIMEOUT_SECONDS,
                )

                stream_started = True
                async for chunk in stream:
                    # Groq delta handling
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response_content += delta
                        yield ChatStreamResponse(delta=delta)

                # Successful completion
                break

            except (RateLimitError, APIStatusError) as e:
                # Only retry if we haven't started streaming yet
                if stream_started:
                    logger.error("groq_stream_interrupted", error=str(e))
                    yield ChatStreamResponse(
                        error="Connection to AI was lost mid-stream."
                    )
                    return

                attempt += 1
                if attempt >= self.max_retries:
                    logger.error(
                        "groq_api_error_exhausted", error=str(e), attempt=attempt
                    )
                    yield ChatStreamResponse(
                        error="The AI service is currently busy. Please try again in a moment."
                    )
                    return

                sleep_time = (2**attempt) + random.uniform(0, 1)
                logger.warning(
                    "groq_api_retry", attempt=attempt, error=str(e), sleeping=sleep_time
                )
                await asyncio.sleep(sleep_time)

            except asyncio.TimeoutError:
                logger.error("chat_timeout", session_id=str(session_id))
                yield ChatStreamResponse(error="Request timed out.")
                return

            except asyncio.CancelledError:
                logger.warning("chat_streaming_cancelled", session_id=str(session_id))
                raise

            except Exception as e:
                logger.error(
                    "chat_generation_failed", error=str(e), session_id=str(session_id)
                )
                yield ChatStreamResponse(error="An error occurred during generation.")
                return

        # 6. Final Chunk with Citations
        yield ChatStreamResponse(is_final=True, citations=citations)

        # 7. Persist Assistant Message
        latency = (time.perf_counter() - start_time) * 1000
        await self.chat_repo.create_message(
            ChatMessageCreate(
                session_id=session_id,
                user_id=user_id,
                role=MessageRole.ASSISTANT,
                content=full_response_content,
                citations=[c.model_dump(mode='json') for c in citations],
                source_chunk_ids=source_chunk_ids,
                model_name=settings.GROQ_CHAT_MODEL,
                token_count=count_tokens(full_response_content),
                latency_ms=latency,
                prompt_version=settings.CHAT_SYSTEM_PROMPT_VERSION,
            )
        )
