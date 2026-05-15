"""
Async SQLAlchemy session management.

Provides:
  - engine         : A single async engine shared across the app lifetime.
  - AsyncSessionLocal: Session factory for creating DB sessions.
  - get_db()       : FastAPI dependency that yields a scoped async session.
  - check_db_connection(): Health check helper called at startup.

All database I/O MUST go through get_db() to guarantee proper
transaction lifecycle and connection pool management.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import text

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# Engine — created once at module import time.
# Pool tuned for production; override via env vars if needed.
# ---------------------------------------------------------------------------
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.is_development,          # SQL query logging in dev only
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,                    # validate connections before use
    pool_recycle=1800,                     # recycle connections every 30 min
    future=True,
)

# ---------------------------------------------------------------------------
# Session factory — use this via get_db(), never directly.
# ---------------------------------------------------------------------------
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,                # avoid lazy-load errors post-commit
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a scoped async database session.

    Automatically commits on success and rolls back + closes on any error.

    Usage:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Verify the database is reachable.

    Returns:
        True if the connection succeeds, False otherwise.

    Raises:
        Does NOT raise — logs the error and returns False so the health
        check endpoint can report degraded status gracefully.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("database.connection_ok")
        return True
    except Exception as exc:
        logger.error("database.connection_failed", error=str(exc))
        return False
