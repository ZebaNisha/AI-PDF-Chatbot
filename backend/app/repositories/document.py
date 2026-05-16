import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj_in: DocumentCreate) -> Document:
        db_obj = Document(
            user_id=obj_in.user_id,
            original_filename=obj_in.original_filename,
            stored_filename=obj_in.stored_filename,
            storage_url=obj_in.storage_url,
            file_size=obj_in.file_size,
            mime_type=obj_in.mime_type,
            status=obj_in.status,
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, id: uuid.UUID) -> Document | None:
        stmt = select(Document).where(Document.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_multi_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Document]:
        stmt = select(Document).where(Document.user_id == user_id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, db_obj: Document, obj_in: DocumentUpdate) -> Document:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: uuid.UUID) -> None:
        stmt = select(Document).where(Document.id == id)
        result = await self.session.execute(stmt)
        db_obj = result.scalars().first()
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.commit()
