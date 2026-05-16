import uuid
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chat import ChatMessage
from app.schemas.chat import ChatMessageCreate


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_message(self, message_in: ChatMessageCreate) -> ChatMessage:
        db_message = ChatMessage(**message_in.model_dump())
        self.session.add(db_message)
        await self.session.commit()
        await self.session.refresh(db_message)
        return db_message

    async def get_session_history(
        self, session_id: uuid.UUID, limit: int = 10
    ) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        # Reverse to get chronological order for the LLM
        return list(reversed(result.scalars().all()))

    async def delete_session(self, session_id: uuid.UUID):
        stmt = delete(ChatMessage).where(ChatMessage.session_id == session_id)
        await self.session.execute(stmt)
        await self.session.commit()
