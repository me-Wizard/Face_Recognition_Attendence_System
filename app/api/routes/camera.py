"""
app/api/routes/camera.py
------------------------
Camera API routes.

Rule: Zero OpenCV logic here.
Routes delegate entirely to detection_service.

Endpoints:
    GET /camera/start  — Launch the real-time detection loop in a background thread.
"""

import threading

from fastapi import APIRouter, HTTPException

from app.services.detection_service import get_current_status, run_detection_loop

router = APIRouter()

# Thread reference — kept module-level so we can check if one is already running
_camera_thread: threading.Thread | None = None


@router.get("/start", summary="Start real-time face detection loop")
def start_camera():
    """
    Launch the webcam face-detection loop in a background thread.

    The loop runs until the user presses **'q'** inside the OpenCV window.

    - Opens webcam device 0.
    - Applies CLAHE preprocessing every frame.
    - Runs Haar Cascade detection.
    - Draws bounding boxes and shows cropped face windows.

    Returns a confirmation that the thread has been started.
    If detection is already running, returns HTTP 409.
    """
    global _camera_thread

    status = get_current_status()
    if status["running"]:
        raise HTTPException(
            status_code=409,
            detail="Detection loop is already running. "
                   "Press 'q' in the camera window to stop it first.",
        )

    _camera_thread = threading.Thread(
        target=run_detection_loop,
        kwargs={"device_index": 0},
        daemon=True,          # Thread dies automatically when the server stops
        name="DetectionLoop",
    )
    _camera_thread.start()

    return {
        "message": "Face detection loop started.",
        "instruction": "Press 'q' in the OpenCV window to stop.",
        "thread": _camera_thread.name,
    }
