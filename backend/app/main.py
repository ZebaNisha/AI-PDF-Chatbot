import traceback
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.routes import health, auth
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging

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
    logger.info("application.startup", environment=settings.ENVIRONMENT, version=settings.APP_VERSION)
    
    # Place global initialisations here (e.g., Redis pool, Qdrant client connection check)
    
    yield  # Application runs during this yield
    
    # Place global teardown here
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
    # app.include_router(documents.router)
    # app.include_router(chat.router)

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
