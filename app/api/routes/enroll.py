"""
app/api/routes/enroll.py
------------------------
Enrollment API routes.

Rule: Zero OpenCV / AI logic here.
Routes only validate input and delegate to enrollment_service.

Endpoints:
    POST /enroll/start          — Begin enrollment for a new person.
    DELETE /enroll/{employee_id} — Remove a person from the system.
    GET  /enroll/{employee_id}   — Check if a person is enrolled.
"""

import threading

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.db import crud
from app.services.enrollment_service import enroll_user

router = APIRouter()

# Track whether an enrollment session is already running
_enrollment_lock = threading.Lock()
_enrollment_running = False


# ── Request schema ─────────────────────────────────────────────────────────────

class EnrollRequest(BaseModel):
    name:        str = Field(..., min_length=2, max_length=120, example="Hassan Ahmed")
    employee_id: str = Field(..., min_length=1, max_length=60,  example="EMP-001")
    department:  str = Field(..., min_length=1, max_length=120, example="Engineering")


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/start", summary="Enroll a new person — opens webcam to capture face samples")
def start_enrollment(
    payload: EnrollRequest,
    db: Session = Depends(get_db),
):
    """
    Start the enrollment pipeline for a new employee / student.

    **Flow:**
    1. Validates the request body.
    2. Checks that `employee_id` is not already enrolled.
    3. Opens the webcam in a foreground loop (blocking while the window is open).
    4. Collects **5 good-quality face samples**, extracts FaceNet embeddings.
    5. Saves the user + embeddings to PostgreSQL.
    6. Returns an enrollment summary.

    **Camera window controls:**
    - Press **`q`** to cancel enrollment early.

    **Quality filters applied per frame:**
    - Exactly one face must be visible.
    - Face must be at least 80×80 px.
    - Frame must not be blurry (Laplacian variance ≥ 80).
    - New sample must not be near-duplicate of existing samples.
    """
    global _enrollment_running

    with _enrollment_lock:
        if _enrollment_running:
            raise HTTPException(
                status_code=409,
                detail="An enrollment session is already in progress.",
            )
        _enrollment_running = True

    try:
        result = enroll_user(
            db=db,
            name=payload.name,
            employee_id=payload.employee_id,
            department=payload.department,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        with _enrollment_lock:
            _enrollment_running = False

    if not result["success"]:
        raise HTTPException(status_code=422, detail=result["message"])

    return result


@router.get("/{employee_id}", summary="Check enrollment status of an employee")
def check_enrollment(
    employee_id: str,
    db: Session = Depends(get_db),
):
    """
    Return enrollment details for a given employee_id.
    Returns HTTP 404 if the person is not enrolled.
    """
    user = crud.get_user_by_employee_id(db, employee_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Employee ID '{employee_id}' is not enrolled.",
        )
    return {
        "enrolled": True,
        "user_id":     str(user.id),
        "name":        user.name,
        "employee_id": user.employee_id,
        "department":  user.department,
        "enrolled_at": user.enrolled_at.isoformat(),
        "embedding_count": len(user.embeddings),
    }


@router.delete("/{employee_id}", summary="Remove a person and all their embeddings")
def delete_enrollment(
    employee_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a user and all associated face embeddings from the database.
    Returns HTTP 404 if not found.
    """
    deleted = crud.delete_user(db, employee_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Employee ID '{employee_id}' not found.",
        )
    return {"deleted": True, "employee_id": employee_id}
