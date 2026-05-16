import uuid
from typing import Any, Dict, List, Optional, Tuple
import structlog
from qdrant_client.http import models

from app.core.qdrant import qdrant_client
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class VectorSearchService:
    """
    Low-level service for interacting with Qdrant to perform semantic searches.
    Enforces security via user_id filtering.
    """

    def __init__(self, collection_name: Optional[str] = None):
        self.collection_name = collection_name or settings.QDRANT_COLLECTION

    async def search_vectors(
        self,
        query_vector: List[float],
        user_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> List[models.ScoredPoint]:
        """
        Perform semantic search in Qdrant with security and quality filtering.
        """
        top_k = top_k or settings.RETRIEVAL_TOP_K
        score_threshold = score_threshold or settings.RETRIEVAL_SCORE_THRESHOLD

        # 1. Build Security & Metadata Filters
        # MUST filter by user_id to prevent cross-user leakage
        must_filters = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=str(user_id))
            )
        ]

        # Optional: filter by specific documents
        if document_ids:
            must_filters.append(
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchAny(any=[str(d_id) for d_id in document_ids])
                )
            )

        qdrant_filter = models.Filter(must=must_filters)

        try:
            # 2. Execute Semantic Search
            results = await qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=qdrant_filter,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )

            logger.info(
                "vector_search_executed",
                user_id=str(user_id),
                results_count=len(results),
                top_k=top_k,
                threshold=score_threshold
            )
            return results

        except Exception as e:
            logger.error("vector_search_failed", error=str(e), user_id=str(user_id))
            # Handle potential malformed vector protection here if needed
            # For now, we propagate the error or return empty results
            return []
