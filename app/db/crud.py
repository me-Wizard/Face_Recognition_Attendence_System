"""
app/db/crud.py
--------------
All database read/write operations.

Rules:
- No business logic here — only DB operations.
- Every function takes a SQLAlchemy Session as first argument.
- Routes never call these directly — they go through services.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import User, FaceEmbedding


# ── Users ─────────────────────────────────────────────────────────────────────

def get_user_by_employee_id(db: Session, employee_id: str) -> Optional[User]:
    """Return a User row by employee_id, or None if not found."""
    return db.query(User).filter(User.employee_id == employee_id).first()


def create_user(
    db: Session,
    name: str,
    employee_id: str,
    department: str,
) -> User:
    """
    Insert a new user row and return it.
    Raises ValueError if employee_id already exists.
    """
    existing = get_user_by_employee_id(db, employee_id)
    if existing:
        raise ValueError(f"Employee ID '{employee_id}' is already enrolled.")

    user = User(
        id=uuid.uuid4(),
        name=name,
        employee_id=employee_id,
        department=department,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, employee_id: str) -> bool:
    """Delete a user and all their embeddings. Returns True if deleted."""
    user = get_user_by_employee_id(db, employee_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


# ── Embeddings ────────────────────────────────────────────────────────────────

def save_embedding(
    db: Session,
    user_id: uuid.UUID,
    vector: list[float],
    sample_idx: int,
) -> FaceEmbedding:
    """Insert one embedding row linked to user_id."""
    emb = FaceEmbedding(
        user_id=user_id,
        vector=vector,
        sample_idx=sample_idx,
    )
    db.add(emb)
    db.commit()
    db.refresh(emb)
    return emb


def save_all_embeddings(
    db: Session,
    user_id: uuid.UUID,
    vectors: list[list[float]],
) -> list[FaceEmbedding]:
    """
    Bulk-insert all embeddings for a user in a single transaction.
    vectors[0] → sample_idx=1, vectors[1] → sample_idx=2, etc.
    """
    rows = [
        FaceEmbedding(user_id=user_id, vector=vec, sample_idx=idx + 1)
        for idx, vec in enumerate(vectors)
    ]
    db.bulk_save_objects(rows)
    db.commit()
    return rows


def get_embeddings_by_user(db: Session, user_id: uuid.UUID) -> list[FaceEmbedding]:
    """Return all embedding rows for a given user UUID."""
    return (
        db.query(FaceEmbedding)
        .filter(FaceEmbedding.user_id == user_id)
        .order_by(FaceEmbedding.sample_idx)
        .all()
    )


def get_all_users_with_embeddings(db: Session) -> list[User]:
    """Return all users who have at least one embedding (for recognition use)."""
    return (
        db.query(User)
        .join(FaceEmbedding)
        .distinct()
        .all()
    )

# ── Recognition ───────────────────────────────────────────────────────────────

def get_user_by_id(db: Session, user_id) -> Optional[User]:
    """Return a User row by UUID primary key, or None if not found."""
    return db.query(User).filter(User.id == user_id).first()


def get_all_embeddings(db: Session) -> list:
    """
    Fetch every embedding row joined with its user data.
    Returns a flat list of dicts — one entry per stored embedding vector.

    Returns:
        List of dicts with keys: user_id, employee_id, name, department, vector
    """
    rows = (
        db.query(FaceEmbedding, User)
        .join(User, FaceEmbedding.user_id == User.id)
        .all()
    )

    result = []
    for embedding, user in rows:
        result.append({
            "user_id":     str(user.id),
            "employee_id": user.employee_id,
            "name":        user.name,
            "department":  user.department,
            "vector":      embedding.vector,
        })

    return result