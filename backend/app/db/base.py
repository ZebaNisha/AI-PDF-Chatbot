"""
SQLAlchemy declarative base and shared column mixins.

This module re-exports the Base class and all models to ensure 
they are registered with the metadata for Alembic.
"""

from app.db.base_class import Base  # noqa: F401
from app.db.models.user import User  # noqa: F401
from app.db.models.document import Document  # noqa: F401
from app.db.models.chat import ChatMessage  # noqa: F401
