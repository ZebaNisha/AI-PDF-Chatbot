import asyncio
import traceback
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, documents, health, chat
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.qdrant import init_qdrant
from app.db.base import Base
from app.db.session import engine

# Load configuration early
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events cleanly.
    """
    # 1. Initialize structured logging on startup
    setup_logging()
    logger = get_logger("app.startup")
    print("DEBUG: Logging initialized. Starting background initialization...")
    logger.info("application.startup", environment=settings.ENVIRONMENT, version=settings.APP_VERSION)
    
    # Run heavy initialization in the background so the server can start listening immediately
    async def initialize_services():
        # 2. Initialize Embedding Model
        try:
            print(f"DEBUG: Background - Loading embedding model: {settings.EMBEDDING_MODEL}")
            from app.services.embedding import EmbeddingService
            embedding_service = EmbeddingService()
            await embedding_service.initialize()
            print("DEBUG: Background - Embedding model ready")
            logger.info("application.embedding_model_ready")
        except Exception as e:
            print(f"DEBUG: Background - Embedding model failed: {e}")
            logger.error("application.embedding_model_init_failed", error=str(e))

        # 3. Initialize Qdrant Vector Database
        try:
            print(f"DEBUG: Background - Initializing Qdrant at: {settings.QDRANT_URL}")
            await init_qdrant()
            print("DEBUG: Background - Qdrant initialized")
            logger.info("application.qdrant_initialized")
        except Exception as e:
            print(f"DEBUG: Background - Qdrant failed: {e}")
            logger.error("application.qdrant_initialization_failed", error=str(e))
        
        # 4. Create Database Tables (Development only)
        if settings.is_development:
            try:
                print("DEBUG: Background - Creating database tables")
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                print("DEBUG: Background - Database tables created")
                logger.info("application.database_tables_created")
            except Exception as e:
                print(f"DEBUG: Background - Database failed: {e}")
                logger.error("application.database_table_creation_failed", error=str(e))

    # Trigger background initialization
    init_task = asyncio.create_task(initialize_services())
    
    yield  # Application starts listening HERE
    
    # Cleanup
    init_task.cancel()
    logger = get_logger("app.shutdown")
    logger.info("application.shutdown")


# ---------------------------------------------------------------------------
# FastAPI Application Factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    """
    Factory to create and configure the FastAPI application instance.
    Ensures modularity and easier testing.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI PDF Chatbot Backend API",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
    )

    # Configure CORS
    if settings.ALLOWED_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register Routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(chat.router)

    @app.get("/")
    async def root():
        return {
            "message": "AI PDF Chatbot API is online!",
            "status": "active",
            "version": settings.APP_VERSION
        }

    # -----------------------------------------------------------------------
    # Global Exception Handlers
    # -----------------------------------------------------------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Fallback exception handler to prevent unhandled app crashes and log errors."""
        logger = get_logger("app.exceptions")
        
        # Log the full stack trace for debugging
        logger.error(
            "unhandled_exception", 
            error=str(exc),
            path=request.url.path,
            method=request.method,
            traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        )
        
        # Never leak internal error details in production
        error_detail = "Internal Server Error" if settings.is_production else str(exc)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": error_detail},
        )

    return app


# The ASGI application instance to be run by Uvicorn/Gunicorn
app = create_app()
