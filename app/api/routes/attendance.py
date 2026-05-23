#C:\Attencence_System\app\api\routes\attendance.py

"""
app/api/routes/attendance.py
-----------------------------
Attendance API routes.

Endpoints:
    GET /attendance/today   — return today's full attendance list
    GET /attendance/status  — return current attendance system state

Rules:
- No OpenCV logic here.
- No direct DB calls — only through services or crud.
- Thin routes only.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.db import crud
from app.services import attendance_service

router = APIRouter()


@router.get("/today")
def get_today_attendance(db: Session = Depends(get_db)):
    """
    Return all attendance records marked today.
    """
    records = crud.get_today_attendance(db)
    return {
        "date":    str(__import__("datetime").date.today()),
        "count":   len(records),
        "records": records,
    }


@router.get("/status")
def get_attendance_status():
    """
    Return current in-memory attendance system state.
    No DB call needed — all state lives in attendance_service memory.
    """
    return attendance_service.get_system_status()