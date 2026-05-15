from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.db.session import get_db, check_db_connection
from app.core.config import get_settings

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
    
    # Placeholder for other checks (Redis, Qdrant, etc.)
    # redis_ok = await check_redis_connection()
    # qdrant_ok = await check_qdrant_connection()
    
    all_ok = db_ok # and redis_ok and qdrant_ok
    
    status_code = 200 if all_ok else 503
    
    return {
        "status": "ok" if all_ok else "degraded",
        "services": {
            "database": "up" if db_ok else "down",
            # "redis": "up" if redis_ok else "down",
            # "qdrant": "up" if qdrant_ok else "down",
        }
    }
