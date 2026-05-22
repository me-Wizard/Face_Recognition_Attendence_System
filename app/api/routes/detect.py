"""
app/api/routes/detect.py
------------------------
Detection status API routes.

Rule: Zero OpenCV logic here.
Routes delegate entirely to detection_service.

Endpoints:
    GET /detect/status  — Return the current detection state snapshot.
"""

from fastapi import APIRouter

from app.services.detection_service import get_current_status

router = APIRouter()


@router.get("/status", summary="Get current face detection status")
def detection_status():
    """
    Return a real-time snapshot of the face detection state.

    Response fields:
    - **running**: True while the camera loop is active.
    - **face_detected**: True if at least one face was seen in the most recent frame.
    - **face_count**: Number of faces detected in the most recent frame.
    - **status_label**: Human-readable string — "Face Detected" or "No Face Detected".
    """
    state = get_current_status()
    state["status_label"] = (
        "Face Detected" if state["face_detected"] else "No Face Detected"
    )
    return state
