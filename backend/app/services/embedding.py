import asyncio
import hashlib
import threading
from typing import Any, Dict, List, Optional, Tuple

import structlog

from app.core.config import get_settings
from app.schemas.chunk import DocumentChunk

logger = structlog.get_logger(__name__)
settings = get_settings()


class EmbeddingService:
    """
    Thread-safe singleton service for generating local embeddings.
    Uses SentenceTransformers with GPU acceleration if available.
    """

    _instance: Optional["EmbeddingService"] = None
    _lock = threading.Lock()
    _model: Optional["SentenceTransformer"] = None

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingService, cls).__new__(cls)
            return cls._instance

    def __init__(self, batch_size: int = 32):
        # Ensure initialization logic only runs once
        if not hasattr(self, "initialized"):
            self.batch_size = batch_size
            self.model_name = settings.EMBEDDING_MODEL
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.cache: Dict[str, List[float]] = {}  # content_hash -> embedding
            self.initialized = True
            logger.info(
                "embedding_service_initialized",
                device=self.device,
                model=self.model_name,
                batch_size=self.batch_size,
            )

    def _load_model(self):
        """Internal method to load the model into memory."""
        if self._model is None:
            logger.info("loading_embedding_model_start", model=self.model_name)
            try:
                # Use a local lock to prevent multiple threads from loading simultaneously
                with self._lock:
                    from sentence_transformers import SentenceTransformer
                    if self._model is None:
                        self._model = SentenceTransformer(self.model_name, device=self.device)
                logger.info("loading_embedding_model_complete")
            except Exception as e:
                logger.error("loading_embedding_model_failed", error=str(e))
                raise

    async def initialize(self):
        """
        Loads the model and performs a warmup embedding.
        This should be called during application startup (lifespan).
        """
        try:
            await asyncio.to_thread(self._load_model)
            await self.warmup()
        except Exception as e:
            logger.error("embedding_service_init_failed", error=str(e))
            # We don't raise here to allow the app to start, but health check will fail

    async def warmup(self):
        """Performs a test embedding to ensure model readiness."""
        logger.info("embedding_warmup_start")
        try:
            await self.embed_query("warmup test sentence")
            logger.info("embedding_warmup_complete")
        except Exception as e:
            logger.error("embedding_warmup_failed", error=str(e))

    def _compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async def embed_query(self, text: str) -> List[float]:
        """Generates embedding for a single query string."""
        if not text or not text.strip():
            return []

        embeddings = await self.embed_documents([text])
        return embeddings[0] if embeddings else []

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of strings.
        Wraps the blocking SentenceTransformer.encode in a thread.
        """
        if not texts:
            return []

        if self._model is None:
            await asyncio.to_thread(self._load_model)

        try:
            # Move blocking CPU/GPU work to a separate thread
            embeddings = await asyncio.to_thread(
                self._model.encode,
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error("embedding_generation_failed", error=str(e))
            raise

    async def process_chunks(
        self, chunks: List[DocumentChunk]
    ) -> Tuple[List[Dict[str, Any]], List[DocumentChunk]]:
        """
        Processes a list of DocumentChunks into embeddings.
        Returns a tuple of (successful_results, failed_chunks).
        """
        successful = []
        failed = []

        # 1. Filter out invalid chunks
        valid_indices = []
        for i, chunk in enumerate(chunks):
            if not chunk.text or not chunk.text.strip():
                failed.append(chunk)
                continue
            valid_indices.append(i)

        if not valid_indices:
            return successful, failed

        # 2. Check cache and identify what needs embedding
        to_embed_map = {}  # index -> text
        for idx in valid_indices:
            chunk = chunks[idx]
            content_hash = self._compute_hash(chunk.text)
            if content_hash in self.cache:
                successful.append(
                    {
                        "chunk": chunk,
                        "embedding": self.cache[content_hash],
                        "content_hash": content_hash,
                    }
                )
            else:
                to_embed_map[idx] = chunk.text

        if not to_embed_map:
            return successful, failed

        # 3. Generate embeddings for missing ones
        indices = list(to_embed_map.keys())
        texts = [to_embed_map[i] for i in indices]

        try:
            embeddings = await self.embed_documents(texts)
            for i, emb in enumerate(embeddings):
                orig_idx = indices[i]
                chunk = chunks[orig_idx]
                content_hash = self._compute_hash(chunk.text)
                self.cache[content_hash] = emb
                successful.append(
                    {
                        "chunk": chunk,
                        "embedding": emb,
                        "content_hash": content_hash,
                    }
                )
            logger.info("batch_embedding_success", count=len(texts))
        except Exception as e:
            logger.error("batch_embedding_failed", error=str(e))
            for idx in indices:
                failed.append(chunks[idx])

        return successful, failed

    @property
    def is_ready(self) -> bool:
        """Checks if the model is loaded."""
        return self._model is not None
