#C:\Attencence_System\app\main.py

"""
app/main.py
-----------
FastAPI application entry point.
Registers all routers and creates DB tables on startup.
"""

from fastapi import FastAPI
from app.api.routes import camera, detect, enroll, recognize
from app.api.routes import attendance, system
from app.db.connection import create_tables

app = FastAPI(
    title="Face Attendance System",
    description=(
        "Real-time face detection + enrollment + recognition + attendance system. "
        "Phase 1: Haar Cascade detection. "
        "Phase 2: FaceNet enrollment with PostgreSQL storage. "
        "Phase 3: Cosine similarity face recognition. "
        "Phase 4: Attendance management with duplicate prevention. "
        "Phase 5: Dashboard, history, export, FPS optimization."
    ),
    version="5.0.0",
)

app.include_router(camera.router,     prefix="/camera",     tags=["Camera"])
app.include_router(detect.router,     prefix="/detect",     tags=["Detection"])
app.include_router(enroll.router,     prefix="/enroll",     tags=["Enrollment"])
app.include_router(recognize.router,  prefix="/recognize",  tags=["Recognition"])
app.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
app.include_router(system.router,     prefix="/system",     tags=["System"])


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/", tags=["Root"])
def root():
    return {
        "system":  "Face Attendance System",
        "version": "5.0.0",
        "status":  "running",
        "docs":    "/docs",
        "phases": {
            "phase1": "Detection   → GET  /camera/start",
            "phase2": "Enrollment  → POST /enroll/start",
            "phase3": "Recognition → POST /recognize  |  GET /recognize/start",
            "phase4": "Attendance  → GET  /attendance/today  |  GET /attendance/status",
            "phase5": "Dashboard   → GET  /attendance/history  |  GET /attendance/absent  |  GET /attendance/export/csv  |  GET /system/status",
        },
    }