import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """
    Structured citation for a retrieved chunk.
    """
    document_id: uuid.UUID
    document_title: Optional[str] = None
    start_page: int
    end_page: int
    chunk_id: uuid.UUID


class RetrievalMetrics(BaseModel):
    """
    Performance metrics for the retrieval operation.
    """
    embedding_latency_ms: float = 0.0
    vector_search_latency_ms: float = 0.0
    rerank_latency_ms: float = 0.0
    total_latency_ms: float = 0.0


class RetrievalResult(BaseModel):
    """
    A single retrieved chunk with its score and metadata.
    """
    text: str
    score: float
    rerank_score: Optional[float] = None
    citation: Citation
    chunk_index: int
    token_count: int
    
    # Debug info
    debug_info: Optional[Dict[str, Any]] = None


class RetrievalResponse(BaseModel):
    """
    The full response from the retrieval pipeline.
    """
    query: str
    results: List[RetrievalResult]
    metrics: RetrievalMetrics
    total_results: int
    
    # Optional debug mode
    filters_applied: Optional[Dict[str, Any]] = None
    raw_response: Optional[Any] = None
