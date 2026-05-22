"""
app/services/detection_service.py
----------------------------------
Detection orchestration service.

This is the ONLY file that imports from both core.camera and core.detector.
It owns the main processing loop and ties together:
    Camera  →  image_utils  →  FaceDetector  →  annotated display

Routes call functions in this module — they never touch OpenCV directly.
"""

import cv2

from app.core.camera import Camera
from app.core.detector import FaceDetector
from app.core.image_utils import (
    apply_clahe,
    draw_bounding_boxes,
    show_cropped_faces,
    to_grayscale,
)

# Module-level detector instance — loaded once, reused across calls
_detector = FaceDetector()

# Tracks the current detection state so /detect/status can read it
_current_status: dict = {
    "running": False,
    "face_detected": False,
    "face_count": 0,
}


def get_current_status() -> dict:
    """
    Return the latest detection status snapshot.

    Called by the /detect/status route.

    Returns:
        dict with keys:
            running       (bool)  – True while the camera loop is active.
            face_detected (bool)  – True if at least one face was seen last frame.
            face_count    (int)   – Number of faces seen in the last frame.
    """
    return dict(_current_status)


def run_detection_loop(device_index: int = 0) -> dict:
    """
    Start the real-time face detection loop.

    Opens the webcam, processes frames continuously until the user
    presses 'q', then releases all resources.

    This function is BLOCKING — it runs inside a thread when called
    from the FastAPI route (see routes/camera.py).

    Frame pipeline per iteration:
        1. Capture raw BGR frame from webcam.
        2. Convert to grayscale.
        3. Apply CLAHE for brightness normalisation.
        4. Run Haar Cascade face detection on the enhanced frame.
        5. Draw bounding boxes + status text on the original BGR frame.
        6. Display cropped/zoomed faces in secondary windows.
        7. Show annotated frame in the main "Face Detection" window.
        8. Update the shared _current_status dict.
        9. Break loop if 'q' is pressed.

    Args:
        device_index: Integer index of the webcam device (default 0).

    Returns:
        Summary dict with total_frames processed and final face_count.
    """
    global _current_status

    total_frames = 0

    with Camera(device_index=device_index) as cam:
        _current_status["running"] = True

        while True:
            # ── 1. Capture ──────────────────────────────────────────────
            frame = cam.read_frame()
            total_frames += 1

            # ── 2. Grayscale conversion ──────────────────────────────────
            gray = to_grayscale(frame)

            # ── 3. CLAHE brightness normalisation ────────────────────────
            enhanced = apply_clahe(gray)

            # ── 4. Face detection ────────────────────────────────────────
            faces = _detector.detect(enhanced)

            # ── 5. Annotate original colour frame ────────────────────────
            annotated = draw_bounding_boxes(frame, faces)

            # ── 6. Show cropped face windows ─────────────────────────────
            show_cropped_faces(frame, faces)

            # ── 7. Display main window ───────────────────────────────────
            cv2.imshow("Face Detection — Press 'q' to quit", annotated)

            # ── 8. Update shared status ──────────────────────────────────
            _current_status["face_detected"] = len(faces) > 0
            _current_status["face_count"] = len(faces)

            # ── 9. Exit on 'q' key ───────────────────────────────────────
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    _current_status["running"] = False
    _current_status["face_detected"] = False
    _current_status["face_count"] = 0

    return {
        "message": "Detection loop finished.",
        "total_frames_processed": total_frames,
        "face_count_at_exit": 0,
    }
