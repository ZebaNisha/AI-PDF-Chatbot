import uuid
import time
import unicodedata
from typing import List, Optional, Tuple, Dict, Any

import structlog
from app.core.config import get_settings
from app.services.embedding import EmbeddingService
from app.services.vector_search import VectorSearchService
from app.schemas.retrieval import (
    RetrievalResponse, 
    RetrievalResult, 
    Citation, 
    RetrievalMetrics
)
from app.utils.token_counter import count_tokens

logger = structlog.get_logger(__name__)
settings = get_settings()


class RetrievalService:
    """
    High-level service that orchestrates the retrieval process.
    Handles embedding, search, deduplication, diversity, and citations.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_search_service: VectorSearchService,
    ):
        self.embedding_service = embedding_service
        self.vector_search_service = vector_search_service

    def _preprocess_query(self, query: str) -> str:
        """
        Basic query cleaning and normalization.
        """
        if not query:
            return ""
        # Trim and normalize unicode
        query = query.strip()
        query = unicodedata.normalize("NFKC", query)
        return query

    async def _rerank_results(
        self, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Placeholder for future reranking stage.
        Currently returns results unchanged but ensures they are sorted by score.
        """
        # Future: Integrate with Cohere or Cross-Encoder here.
        # Ensure they remain sorted by semantic score (or combined score later)
        return sorted(results, key=lambda x: x.score, reverse=True)

    async def retrieve(
        self,
        query: str,
        user_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        debug: bool = False,
    ) -> RetrievalResponse:
        """
        Execute the full retrieval pipeline with security, quality, and diversity controls.
        """
        start_total = time.perf_counter()
        metrics = RetrievalMetrics()
        
        # 1. Preprocess Query
        cleaned_query = self._preprocess_query(query)
        if not cleaned_query:
            return RetrievalResponse(
                query=query, 
                results=[], 
                metrics=metrics, 
                total_results=0
            )

        # 2. Embed Query
        start_emb = time.perf_counter()
        # process_chunks returns (successful, failed). We just need the embedding for the query.
        # We'll use a simplified call to the internal _embed_batch_with_retry or similar if available,
        # but EmbeddingService is designed for chunks. Let's add a direct embed method or use it.
        # Actually, let's assume EmbeddingService has a method for single string embedding.
        # If not, I'll use the client directly for simplicity here or update EmbeddingService.
        try:
            # Reusing the existing embedding service logic
            query_vector = await self.embedding_service.embed_query(cleaned_query)
            metrics.embedding_latency_ms = (time.perf_counter() - start_emb) * 1000
        except Exception as e:
            logger.error("query_embedding_failed", error=str(e), user_id=str(user_id))
            return RetrievalResponse(
                query=query, 
                results=[], 
                metrics=metrics, 
                total_results=0
            )

        # 3. Vector Search
        start_search = time.perf_counter()
        raw_results = await self.vector_search_service.search_vectors(
            query_vector=query_vector,
            user_id=user_id,
            document_ids=document_ids,
            top_k=top_k,
            score_threshold=score_threshold
        )
        metrics.vector_search_latency_ms = (time.perf_counter() - start_search) * 1000

        # 4. Post-processing: Deduplication, Diversity, and Formatting
        processed_results: List[RetrievalResult] = []
        seen_texts = set()
        doc_counts = {}
        page_counts = {}
        total_tokens = 0
        
        max_tokens = settings.RETRIEVAL_MAX_CONTEXT_TOKENS
        max_per_doc = settings.RETRIEVAL_MAX_CHUNKS_PER_DOC
        max_per_page = settings.RETRIEVAL_MAX_CHUNKS_PER_PAGE

        for hit in raw_results:
            payload = hit.payload
            text = payload.get("text", "")
            
            # --- Deduplication ---
            if settings.RETRIEVAL_DEDUPLICATION_ENABLED:
                text_hash = payload.get("content_hash") or hash(text)
                if text_hash in seen_texts:
                    continue
                seen_texts.add(text_hash)

            # --- Diversity Control ---
            if settings.RETRIEVAL_DIVERSITY_ENABLED:
                doc_id = payload.get("document_id")
                page_key = f"{doc_id}_{payload.get('start_page')}"
                
                doc_counts[doc_id] = doc_counts.get(doc_id, 0) + 1
                page_counts[page_key] = page_counts.get(page_key, 0) + 1
                
                if doc_counts[doc_id] > max_per_doc or page_counts[page_key] > max_per_page:
                    continue

            # --- Token Control ---
            chunk_tokens = payload.get("token_count") or count_tokens(text)
            if total_tokens + chunk_tokens > max_tokens:
                logger.info("retrieval_token_limit_reached", limit=max_tokens, current=total_tokens)
                break
            
            total_tokens += chunk_tokens

            # --- Formatting & Citation ---
            citation = Citation(
                document_id=uuid.UUID(payload["document_id"]),
                document_title=payload.get("document_title"), # Optional
                start_page=payload["start_page"],
                end_page=payload["end_page"],
                chunk_id=uuid.UUID(payload["chunk_id"])
            )

            result = RetrievalResult(
                text=text,
                score=hit.score,
                citation=citation,
                chunk_index=payload["chunk_index"],
                token_count=chunk_tokens,
                debug_info=payload if debug else None
            )
            processed_results.append(result)

        # 5. Reranking (Placeholder)
        start_rerank = time.perf_counter()
        final_results = await self._rerank_results(processed_results)
        metrics.rerank_latency_ms = (time.perf_counter() - start_rerank) * 1000

        metrics.total_latency_ms = (time.perf_counter() - start_total) * 1000

        return RetrievalResponse(
            query=query,
            results=final_results,
            metrics=metrics,
            total_results=len(final_results),
            filters_applied={"user_id": str(user_id), "document_ids": [str(d) for d in document_ids] if document_ids else None} if debug else None,
            raw_response=raw_results if debug else None
        )
