from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.db.session import get_db, check_db_connection
from app.core.config import get_settings
from app.core.qdrant import check_connection as check_qdrant_connection
from app.services.embedding import EmbeddingService

router = APIRouter(prefix="/health", tags=["System"])
settings = get_settings()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic application health check.
    Does not verify downstream dependencies like DB or Redis.
    Suitable for load balancer ping.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/deep")
async def deep_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Deep health check that verifies connectivity to critical downstream services.
    Suitable for liveness/readiness probes.
    """
    db_ok = await check_db_connection()
    qdrant_ok = await check_qdrant_connection()

    # Check local embedding model status
    embedding_service = EmbeddingService()
    embedding_ok = embedding_service.is_ready

    # Basic Groq configuration check
    groq_ok = bool(settings.GROQ_API_KEY)

    all_ok = db_ok and qdrant_ok and embedding_ok and groq_ok

    return {
        "status": "ok" if all_ok else "degraded",
        "services": {
            "database": "up" if db_ok else "down",
            "qdrant": "up" if qdrant_ok else "down",
            "embedding_model": "loaded" if embedding_ok else "not_ready",
            "groq_api": "configured" if groq_ok else "unconfigured",
        },
    }
