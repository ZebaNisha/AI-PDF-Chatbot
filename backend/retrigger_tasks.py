import asyncio
import uuid
from app.worker.tasks import process_document_task
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.db.models.document import Document, DocumentStatus

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Document).where(Document.status == DocumentStatus.PENDING)
        )
        docs = result.scalars().all()
        for doc in docs:
            print(f"Re-triggering task for {doc.original_filename} ({doc.id})")
            process_document_task.delay(str(doc.id))

if __name__ == "__main__":
    asyncio.run(main())
