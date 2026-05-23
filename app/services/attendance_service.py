#C:\Attencence_System\app\services\attendance_service.py

"""
app/services/attendance_service.py
------------------------------------
Complete attendance business logic.

Responsibilities:
- Receive recognized user from recognition pipeline.
- Verify stable recognition across consecutive frames.
- Verify cooldown window has passed.
- Check duplicate attendance for today.
- Mark attendance via crud layer.
- Return structured attendance status response.
- Provide attendance history, absent users, and CSV export.

State maintained in module-level memory (no DB for frame tracking).
"""

import io
import time
import uuid
from datetime import date
from typing import Optional

import pandas as pd
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import crud

# ── Configuration ─────────────────────────────────────────────────────────────

STABLE_FRAME_REQUIRED = 5
COOLDOWN_SECONDS      = 15

# ── In-memory state ───────────────────────────────────────────────────────────

_frame_counter:    dict[str, int]   = {}
_cooldown_tracker: dict[str, float] = {}
_last_status:      dict[str, dict]  = {}


# ── Core attendance logic ─────────────────────────────────────────────────────

def process_recognition(
    db: Session,
    employee_id: str,
    user_id: str,
    name: str,
    confidence: float,
) -> dict:
    if _is_in_cooldown(employee_id):
        return _last_status.get(employee_id, {
            "status":      "cooldown",
            "message":     "Attendance Marked",
            "name":        name,
            "employee_id": employee_id,
            "confidence":  confidence,
        })

    _frame_counter[employee_id] = _frame_counter.get(employee_id, 0) + 1
    current_count = _frame_counter[employee_id]

    if current_count < STABLE_FRAME_REQUIRED:
        return {
            "status":      "recognizing",
            "message":     f"Recognized ({current_count}/{STABLE_FRAME_REQUIRED})",
            "name":        name,
            "employee_id": employee_id,
            "confidence":  confidence,
        }

    uid = uuid.UUID(user_id)

    already_marked = crud.check_attendance_today(db, uid)
    if already_marked:
        _set_cooldown(employee_id)
        _reset_frame_counter(employee_id)
        status = {
            "status":      "exists",
            "message":     "Already Marked Present",
            "name":        name,
            "employee_id": employee_id,
            "confidence":  confidence,
        }
        _last_status[employee_id] = status
        return status

    crud.mark_attendance(db, uid, status="present")
    _set_cooldown(employee_id)
    _reset_frame_counter(employee_id)

    status = {
        "status":      "success",
        "message":     "Attendance Marked",
        "name":        name,
        "employee_id": employee_id,
        "confidence":  confidence,
    }
    _last_status[employee_id] = status
    return status


def reset_frame_counter_for(employee_id: str) -> None:
    _frame_counter.pop(employee_id, None)


def get_system_status() -> dict:
    return {
        "stable_frame_required": STABLE_FRAME_REQUIRED,
        "cooldown_seconds":      COOLDOWN_SECONDS,
        "active_frame_counters": dict(_frame_counter),
        "users_in_cooldown": [
            eid for eid, ts in _cooldown_tracker.items()
            if time.time() - ts < COOLDOWN_SECONDS
        ],
    }


# ── Dashboard services ────────────────────────────────────────────────────────

def get_today_attendance(db: Session) -> dict:
    """
    Return today's full attendance list with count and date.
    """
    records = crud.get_today_attendance(db)
    return {
        "date":    str(date.today()),
        "count":   len(records),
        "records": records,
    }


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
    return crud.get_attendance_history(
        db=db,
        employee_id=employee_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size,
    )


def get_absent_users(db: Session) -> dict:
    """
    Return all users not marked present today.
    """
    absent = crud.get_absent_users(db)
    return {
        "date":   str(date.today()),
        "count":  len(absent),
        "absent": absent,
    }


def export_attendance_csv(db: Session) -> StreamingResponse:
    """
    Generate and return today's attendance as a downloadable CSV.
    Uses pandas to build the CSV in memory — no file written to disk.
    """
    records = crud.get_today_attendance(db)

    if not records:
        df = pd.DataFrame(columns=["name", "employee_id", "department", "date", "time", "status"])
    else:
        df = pd.DataFrame(records)[["name", "employee_id", "department", "date", "time", "status"]]

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    filename = f"attendance_{date.today()}.csv"

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _is_in_cooldown(employee_id: str) -> bool:
    last_marked = _cooldown_tracker.get(employee_id)
    if last_marked is None:
        return False
    return (time.time() - last_marked) < COOLDOWN_SECONDS


def _set_cooldown(employee_id: str) -> None:
    _cooldown_tracker[employee_id] = time.time()


def _reset_frame_counter(employee_id: str) -> None:
    _frame_counter.pop(employee_id, None)