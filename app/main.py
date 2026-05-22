"""
app/main.py
-----------
FastAPI application entry point.
Registers all routers and configures the app lifecycle.
"""

from fastapi import FastAPI
from app.api.routes import camera, detect

app = FastAPI(
    title="Face Attendance System",
    description="Real-time face detection system built for attendance tracking. "
                "Powered by OpenCV Haar Cascade and CLAHE preprocessing.",
    version="1.0.0",
)

# Register route modules
app.include_router(camera.router, prefix="/camera", tags=["Camera"])
app.include_router(detect.router, prefix="/detect", tags=["Detection"])


@app.get("/", tags=["Root"])
def root():
    return {
        "system": "Face Attendance System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
