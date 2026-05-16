"""
Structured logging module.

Configures structlog for JSON output in production and
colourised console output in development.

Usage:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("event", key="value")
"""

import logging
import sys
from typing import Any

import structlog

from app.core.config import get_settings


def _get_processors(is_production: bool) -> list[Any]:
    """Return the structlog processor chain for the given environment."""
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if is_production:
        return shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    return shared_processors + [
        structlog.dev.ConsoleRenderer(colors=True),
    ]


def setup_logging() -> None:
    """
    Configure structlog and the standard library logging integration.

    Must be called once at application startup (inside lifespan).
    """
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # --- stdlib logging → structlog bridge ---
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    processors = _get_processors(settings.is_production)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Return a bound structlog logger.

    Args:
        name: Logger name (typically __name__).

    Returns:
        A structlog BoundLogger instance.
    """
    return structlog.get_logger(name)
