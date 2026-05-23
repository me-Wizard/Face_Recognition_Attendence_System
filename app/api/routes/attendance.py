#C:\Attencence_System\app\api\routes\attendance.py

"""
app/api/routes/attendance.py
-----------------------------
Attendance API routes.

Endpoints:
    GET /attendance/today        — today's full attendance list
    GET /attendance/status       — in-memory system state
    GET /attendance/history      — paginated history with filters
    GET /attendance/absent       — users not marked today
    GET /attendance/export/csv   — download today's attendance as CSV

Rules:
- No OpenCV logic here.
- No direct DB calls — only through services.
- Thin routes only.
"""

from datetime import date as date_type
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.services import attendance_service

router = APIRouter()


@router.get("/today")
def get_today_attendance(db: Session = Depends(get_db)):
    return attendance_service.get_today_attendance(db)


@router.get("/status")
def get_attendance_status():
    return attendance_service.get_system_status()


@router.get("/history")
def get_attendance_history(
    employee_id: Optional[str]       = Query(None, description="Filter by employee ID"),
    from_date:   Optional[date_type] = Query(None, description="Start date YYYY-MM-DD"),
    to_date:     Optional[date_type] = Query(None, description="End date YYYY-MM-DD"),
    page:        int                 = Query(1,    ge=1,  description="Page number"),
    page_size:   int                 = Query(20,   ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
):
    return attendance_service.get_attendance_history(
        db=db,
        employee_id=employee_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size,
    )


@router.get("/absent")
def get_absent_users(db: Session = Depends(get_db)):
    return attendance_service.get_absent_users(db)


@router.get("/export/csv", response_class=StreamingResponse)
def export_attendance_csv(db: Session = Depends(get_db)):
    return attendance_service.export_attendance_csv(db)