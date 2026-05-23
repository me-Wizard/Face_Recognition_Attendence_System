"""
app/api/routes/recognize.py
----------------------------
Recognition API routes.

Rule: Zero OpenCV / AI / DB logic here.
Routes only validate input and delegate to recognition_service.

Endpoints:
    POST /recognize         — Single-shot recognition from one webcam frame.
    GET  /recognize/start   — Start continuous live recognition loop.
"""

import threading

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.services.recognition_service import (
    recognize_single_frame,
    run_recognition_loop,
)

router = APIRouter()

_recognition_lock    = threading.Lock()
_recognition_running = False


@router.post("", summary="Single-shot face recognition from one webcam frame")
def recognize(db: Session = Depends(get_db)):
    """
    Capture one frame from the webcam, detect all faces,
    and return recognition results for each face.

    Recognised face response:
        {"matched": true, "name": "...", "employee_id": "...", "confidence": 0.82}

    Unknown face response:
        {"matched": false, "message": "No Match Found", "confidence": 0.54}
    """
    try:
        results = recognize_single_frame(db=db)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recognition error: {exc}")

    if not results:
        return {
            "faces_detected": 0,
            "results": [],
            "message": "No faces detected in frame.",
        }

    return {
        "faces_detected": len(results),
        "results": results,
    }


@router.get("/start", summary="Start continuous live recognition loop")
def start_recognition_loop(db: Session = Depends(get_db)):
    """
    Launch the continuous face recognition loop in a background thread.
    Press 'q' in the OpenCV window to stop.
    """
    global _recognition_running

    with _recognition_lock:
        if _recognition_running:
            raise HTTPException(
                status_code=409,
                detail="Recognition loop is already running. Press 'q' to stop it first.",
            )
        _recognition_running = True

    def _run():
        global _recognition_running
        from app.db.connection import SessionLocal
        thread_db = SessionLocal()
        try:
            run_recognition_loop(db=thread_db)
        finally:
            thread_db.close()
            with _recognition_lock:
                _recognition_running = False

    thread = threading.Thread(target=_run, daemon=True, name="RecognitionLoop")
    thread.start()

    return {
        "message":     "Recognition loop started.",
        "instruction": "Press 'q' in the OpenCV window to stop.",
        "thread":      thread.name,
    }