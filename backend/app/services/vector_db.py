import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

import structlog
from qdrant_client.http import models

from app.core.config import get_settings
from app.core.qdrant import qdrant_client
from app.db.models.document import DocumentStatus
from app.repositories.document import DocumentRepository
from app.schemas.vector import VectorMetadata

logger = structlog.get_logger(__name__)
settings = get_settings()


class VectorDBService:
    def __init__(self, document_repo: DocumentRepository):
        self.collection_name = settings.QDRANT_COLLECTION
        self.document_repo = document_repo

    async def store_vectors(self, document_id: uuid.UUID, successful_embeddings: List[Dict[str, Any]]):
        if not successful_embeddings:
            logger.warning("no_embeddings_to_store", document_id=str(document_id))
            return

        doc = await self.document_repo.get_by_id(document_id)
        if not doc:
            logger.error("document_not_found_for_vectors", document_id=str(document_id))
            return
            
        user_id_str = str(doc.user_id)

        points = []
        for item in successful_embeddings:
            chunk = item["chunk"]
            embedding = item["embedding"]
            content_hash = item["content_hash"]

            # Payload optimization: keep only necessary metadata
            metadata = VectorMetadata(
                chunk_id=str(chunk.chunk_id),
                document_id=str(chunk.document_id),
                user_id=user_id_str,
                text=chunk.text,
                start_page=chunk.start_page,
                end_page=chunk.end_page,
                chunk_index=chunk.chunk_index,
                model_name=settings.EMBEDDING_MODEL,
                embedding_dimension=settings.VECTOR_DIMENSION,
                provider="sentence-transformers",
                created_at=datetime.now(timezone.utc).isoformat(),
                content_hash=content_hash,
                embedding_version="1.1",
                token_count=chunk.token_count,
            ).model_dump()

            points.append(
                models.PointStruct(id=str(chunk.chunk_id), vector=embedding, payload=metadata)
            )

        try:
            # Use upsert to handle re-processing
            await qdrant_client.upsert(collection_name=self.collection_name, points=points)
            logger.info("vectors_upserted_successfully", document_id=str(document_id), count=len(points))

            # Processing status hook -> COMPLETED
            doc = await self.document_repo.get_by_id(document_id)
            if doc:
                from app.schemas.document import DocumentUpdate

                await self.document_repo.update(doc, DocumentUpdate(status=DocumentStatus.COMPLETED))

        except Exception as e:
            logger.error("vectors_upsert_failed", document_id=str(document_id), error=str(e))
            # Processing status hook -> FAILED
            doc = await self.document_repo.get_by_id(document_id)
            if doc:
                from app.schemas.document import DocumentUpdate

                await self.document_repo.update(doc, DocumentUpdate(status=DocumentStatus.FAILED))
            raise

    async def delete_document_vectors(self, document_id: uuid.UUID):
        """
        Internal method to delete all vectors belonging to a document.
        """
        try:
            await qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id", match=models.MatchValue(value=str(document_id))
                            )
                        ]
                    )
                ),
            )
            logger.info("vectors_deleted_successfully", document_id=str(document_id))
        except Exception as e:
            logger.error("vectors_delete_failed", document_id=str(document_id), error=str(e))
            raise
