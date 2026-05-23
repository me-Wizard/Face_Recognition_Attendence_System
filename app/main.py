"""
app/main.py
-----------
FastAPI application entry point.
Registers all routers and creates DB tables on startup.
"""

from fastapi import FastAPI
from app.api.routes import camera, detect, enroll, recognize
from app.db.connection import create_tables

app = FastAPI(
    title="Face Attendance System",
    description=(
        "Real-time face detection + enrollment + recognition system. "
        "Phase 1: Haar Cascade detection. "
        "Phase 2: FaceNet enrollment with PostgreSQL storage. "
        "Phase 3: Cosine similarity face recognition."
    ),
    version="3.0.0",
)

app.include_router(camera.router,    prefix="/camera",    tags=["Camera"])
app.include_router(detect.router,    prefix="/detect",    tags=["Detection"])
app.include_router(enroll.router,    prefix="/enroll",    tags=["Enrollment"])
app.include_router(recognize.router, prefix="/recognize", tags=["Recognition"])


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/", tags=["Root"])
def root():
    return {
        "system":  "Face Attendance System",
        "version": "3.0.0",
        "status":  "running",
        "docs":    "/docs",
        "phases": {
            "phase1": "Detection   → GET  /camera/start",
            "phase2": "Enrollment  → POST /enroll/start",
            "phase3": "Recognition → POST /recognize  |  GET /recognize/start",
        },
    }