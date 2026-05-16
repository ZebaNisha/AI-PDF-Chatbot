"""
Application configuration module.

Loads all settings from environment variables using pydantic-settings.
Provides a cached singleton via get_settings() for dependency injection.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings.

    All values are loaded from environment variables or the .env file.
    Sensitive defaults are intentionally omitted to force explicit configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "AI PDF Chatbot"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"])

    # --- Database (PostgreSQL) ---
    DATABASE_URL: str = ""

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Security ---
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # --- Groq ---
    GROQ_API_KEY: str = ""
    GROQ_CHAT_MODEL: str = "llama-3.3-70b-versatile"

    # --- Local Embeddings ---
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DIMENSION: int = 384

    # --- Qdrant ---
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "pdf_chunks"

    # --- AWS S3 ---
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_REGION: str = "us-east-1"

    # --- PDF Processing ---
    MAX_FILE_SIZE_MB: int = 50
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 120

    # --- Retrieval ---
    RETRIEVAL_TOP_K: int = 10
    RETRIEVAL_SCORE_THRESHOLD: float = 0.10
    RETRIEVAL_MAX_CONTEXT_TOKENS: int = 3000
    RETRIEVAL_MAX_CHUNKS_PER_DOC: int = 5
    RETRIEVAL_MAX_CHUNKS_PER_PAGE: int = 3
    RETRIEVAL_DIVERSITY_ENABLED: bool = True
    RETRIEVAL_DEDUPLICATION_ENABLED: bool = True

    # --- Chat ---
    CHAT_MEMORY_WINDOW: int = 10
    CHAT_MAX_RETRIEVED_CHUNKS: int = 6
    CHAT_TOKEN_BUDGET_RESERVE: int = 500
    CHAT_SYSTEM_PROMPT_VERSION: str = "1.0"
    CHAT_TIMEOUT_SECONDS: int = 60

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _validate_database_url(cls, v: str) -> str:
        """Ensure DATABASE_URL is provided and uses asyncpg driver."""
        if not v:
            return v
        # Automatically convert postgresql:// to postgresql+asyncpg://
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Use this as a FastAPI dependency:
        settings: Settings = Depends(get_settings)
    """
    return Settings()
