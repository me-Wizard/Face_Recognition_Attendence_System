"""
app/main.py
-----------
FastAPI application entry point.
Registers all routers and creates DB tables on startup.
"""

from fastapi import FastAPI
from app.api.routes import camera, detect, enroll
from app.db.connection import create_tables

app = FastAPI(
    title="Face Attendance System",
    description=(
        "Real-time face detection + enrollment system. "
        "Phase 1: Haar Cascade detection. "
        "Phase 2: FaceNet enrollment with PostgreSQL storage."
    ),
    version="2.0.0",
)

# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(camera.router,  prefix="/camera",  tags=["Camera"])
app.include_router(detect.router,  prefix="/detect",  tags=["Detection"])
app.include_router(enroll.router,  prefix="/enroll",  tags=["Enrollment"])


# ── Startup: create tables if they don't exist ────────────────────────────────
@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/", tags=["Root"])
def root():
    return {
        "system": "Face Attendance System",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }
