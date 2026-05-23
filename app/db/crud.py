#C:\Attencence_System\app\db\crud.py

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
from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import User, FaceEmbedding, Attendance


# ── Users ─────────────────────────────────────────────────────────────────────

def get_user_by_employee_id(db: Session, employee_id: str) -> Optional[User]:
    return db.query(User).filter(User.employee_id == employee_id).first()


def create_user(
    db: Session,
    name: str,
    employee_id: str,
    department: str,
) -> User:
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
    rows = [
        FaceEmbedding(user_id=user_id, vector=vec, sample_idx=idx + 1)
        for idx, vec in enumerate(vectors)
    ]
    db.bulk_save_objects(rows)
    db.commit()
    return rows


def get_embeddings_by_user(db: Session, user_id: uuid.UUID) -> list[FaceEmbedding]:
    return (
        db.query(FaceEmbedding)
        .filter(FaceEmbedding.user_id == user_id)
        .order_by(FaceEmbedding.sample_idx)
        .all()
    )


def get_all_users_with_embeddings(db: Session) -> list[User]:
    return (
        db.query(User)
        .join(FaceEmbedding)
        .distinct()
        .all()
    )


# ── Recognition ───────────────────────────────────────────────────────────────

def get_user_by_id(db: Session, user_id) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_all_embeddings(db: Session) -> list:
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


# ── Attendance ────────────────────────────────────────────────────────────────

def check_attendance_today(db: Session, user_id: uuid.UUID) -> bool:
    today = date.today()
    record = (
        db.query(Attendance)
        .filter(
            Attendance.user_id == user_id,
            Attendance.date == today,
        )
        .first()
    )
    return record is not None


def mark_attendance(db: Session, user_id: uuid.UUID, status: str = "present") -> Attendance:
    now = datetime.utcnow()
    record = Attendance(
        user_id=user_id,
        date=now.date(),
        time=now.time(),
        status=status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_today_attendance(db: Session) -> list[dict]:
    today = date.today()
    rows = (
        db.query(Attendance, User)
        .join(User, Attendance.user_id == User.id)
        .filter(Attendance.date == today)
        .order_by(Attendance.time)
        .all()
    )

    result = []
    for record, user in rows:
        result.append({
            "attendance_id": record.id,
            "user_id":       str(user.id),
            "name":          user.name,
            "employee_id":   user.employee_id,
            "department":    user.department,
            "date":          str(record.date),
            "time":          str(record.time),
            "status":        record.status,
        })

    return result


def get_attendance_history(
    db: Session,
    employee_id: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Return paginated attendance history with optional filters.
    """
    query = (
        db.query(Attendance, User)
        .join(User, Attendance.user_id == User.id)
    )

    if employee_id:
        query = query.filter(User.employee_id == employee_id)
    if from_date:
        query = query.filter(Attendance.date >= from_date)
    if to_date:
        query = query.filter(Attendance.date <= to_date)

    total   = query.count()
    offset  = (page - 1) * page_size
    rows    = query.order_by(Attendance.date.desc(), Attendance.time.desc()).offset(offset).limit(page_size).all()

    records = []
    for record, user in rows:
        records.append({
            "attendance_id": record.id,
            "name":          user.name,
            "employee_id":   user.employee_id,
            "department":    user.department,
            "date":          str(record.date),
            "time":          str(record.time),
            "status":        record.status,
        })

    return {
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "pages":     (total + page_size - 1) // page_size,
        "records":   records,
    }


def get_absent_users(db: Session) -> list[dict]:
    """
    Return all enrolled users who have NO attendance record today.
    """
    today = date.today()

    present_user_ids = (
        db.query(Attendance.user_id)
        .filter(Attendance.date == today)
        .subquery()
    )

    absent_users = (
        db.query(User)
        .filter(User.id.notin_(present_user_ids))
        .all()
    )

    return [
        {
            "user_id":     str(u.id),
            "name":        u.name,
            "employee_id": u.employee_id,
            "department":  u.department,
        }
        for u in absent_users
    ]


def get_total_enrolled_users(db: Session) -> int:
    return db.query(User).count()


def get_total_attendance_today(db: Session) -> int:
    return (
        db.query(Attendance)
        .filter(Attendance.date == date.today())
        .count()
    )