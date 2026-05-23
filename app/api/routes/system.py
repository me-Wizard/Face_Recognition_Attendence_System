#C:\Attencence_System\app\api\routes\system.py

"""
app/api/routes/system.py
-------------------------
System monitoring routes.

Endpoints:
    GET /system/status — camera state, FPS, enrolled users, attendance count

Rules:
- No OpenCV logic here.
- No direct DB calls — only through services or crud.
- Thin routes only.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.db import crud
from app.services import recognition_service

router = APIRouter()


@router.get("/status")
def get_system_status(db: Session = Depends(get_db)):
    """
    Return live system metrics.
    """
    perf            = recognition_service.get_performance_stats()
    enrolled_users  = crud.get_total_enrolled_users(db)
    attendance_today = crud.get_total_attendance_today(db)

    return {
        "camera_active":      True,
        "fps":                perf["fps"],
        "avg_latency_ms":     perf["avg_latency_ms"],
        "total_frames":       perf["total_frames"],
        "processed_frames":   perf["processed_frames"],
        "enrolled_users":     enrolled_users,
        "attendance_today":   attendance_today,
        "recognition_active": True,
    }