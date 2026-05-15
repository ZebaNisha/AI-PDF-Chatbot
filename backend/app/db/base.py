"""
SQLAlchemy declarative base and shared column mixins.

All ORM models must inherit from Base so that Alembic can discover
them via metadata. Import and re-export models here after defining them
so Alembic's autogenerate picks them up.

Usage:
    from app.db.base import Base

    class User(Base):
        __tablename__ = "users"
        ...
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models.

    Provides:
      - id       : UUID primary key (server-default via gen_random_uuid())
      - created_at: timezone-aware timestamp, set on INSERT
      - updated_at: timezone-aware timestamp, refreshed on every UPDATE
    """

    # SQLAlchemy 2.x typed mapped columns
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} id={self.id}>"


# ---------------------------------------------------------------------------
# Re-export all models below so Alembic autogenerate can discover them.
# Add each new model import here as the project grows.
# ---------------------------------------------------------------------------
# Example (uncomment when the model is created):
from app.db.models.user import User          # noqa: F401
# from app.db.models.document import Document  # noqa: F401
# from app.db.models.chat import ChatHistory   # noqa: F401
