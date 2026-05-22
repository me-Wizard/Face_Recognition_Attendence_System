"""
app/db/models.py
----------------
SQLAlchemy ORM models.

Tables:
    users       — one row per enrolled person
    embeddings  — one row per embedding vector (5 per user)
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Integer, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name         = Column(String(120), nullable=False)
    employee_id  = Column(String(60),  nullable=False, unique=True, index=True)
    department   = Column(String(120), nullable=False)
    enrolled_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    # one user → many embeddings
    embeddings = relationship(
        "FaceEmbedding",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} employee_id={self.employee_id} name={self.name}>"


class FaceEmbedding(Base):
    __tablename__ = "embeddings"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 128-D FaceNet vector stored as JSONB array of floats
    vector     = Column(JSONB, nullable=False)
    sample_idx = Column(Integer, nullable=False)   # 1–5
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="embeddings")

    def __repr__(self) -> str:
        return f"<FaceEmbedding id={self.id} user_id={self.user_id} sample={self.sample_idx}>"
