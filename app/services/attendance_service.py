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

State maintained in module-level memory (no DB for frame tracking).
"""

import time
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.db import crud

# ── Configuration ─────────────────────────────────────────────────────────────

STABLE_FRAME_REQUIRED = 5       # consecutive frames before marking
COOLDOWN_SECONDS      = 15      # ignore same user for N seconds after marking

# ── In-memory state ───────────────────────────────────────────────────────────

# tracks consecutive recognition count per employee_id
_frame_counter: dict[str, int] = {}

# tracks last attendance-marked timestamp per employee_id
_cooldown_tracker: dict[str, float] = {}

# tracks last attendance result per employee_id for overlay display
_last_status: dict[str, dict] = {}


# ── Public API ────────────────────────────────────────────────────────────────

def process_recognition(
    db: Session,
    employee_id: str,
    user_id: str,
    name: str,
    confidence: float,
) -> dict:
    """
    Called every frame when a face is matched.

    Steps:
        1. Check cooldown — skip if still cooling down.
        2. Increment stable frame counter.
        3. If stable frame threshold reached:
            a. Check duplicate attendance for today.
            b. Mark attendance if not already marked.
        4. Return status dict for overlay rendering.

    Returns:
        dict with keys: status, message, name, employee_id, confidence
    """

    # ── Step 1: Cooldown check ────────────────────────────────────────────────
    if _is_in_cooldown(employee_id):
        return _last_status.get(employee_id, {
            "status":      "cooldown",
            "message":     "Attendance Marked",
            "name":        name,
            "employee_id": employee_id,
            "confidence":  confidence,
        })

    # ── Step 2: Increment frame counter ──────────────────────────────────────
    _frame_counter[employee_id] = _frame_counter.get(employee_id, 0) + 1
    current_count = _frame_counter[employee_id]

    # Not yet stable — still accumulating frames
    if current_count < STABLE_FRAME_REQUIRED:
        return {
            "status":      "recognizing",
            "message":     f"Recognized ({current_count}/{STABLE_FRAME_REQUIRED})",
            "name":        name,
            "employee_id": employee_id,
            "confidence":  confidence,
        }

    # ── Step 3: Stable — attempt attendance marking ───────────────────────────
    uid = uuid.UUID(user_id)

    # Step 3a: Duplicate check
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

    # Step 3b: Mark attendance
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
    """
    Call this when the same face is NOT recognized in a frame.
    Resets the consecutive counter so stability must restart.
    """
    _frame_counter.pop(employee_id, None)


def get_system_status() -> dict:
    """
    Return current in-memory attendance system state.
    Used by GET /attendance/status.
    """
    return {
        "stable_frame_required": STABLE_FRAME_REQUIRED,
        "cooldown_seconds":      COOLDOWN_SECONDS,
        "active_frame_counters": dict(_frame_counter),
        "users_in_cooldown":     [
            eid for eid, ts in _cooldown_tracker.items()
            if time.time() - ts < COOLDOWN_SECONDS
        ],
    }


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