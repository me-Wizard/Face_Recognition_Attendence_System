"""
app/services/recognition_service.py
-------------------------------------
Recognition orchestration service.

Owns the recognition camera loop and ties together:
    Camera → FaceDetector → CLAHE → embedding → DB fetch → matcher → overlay

Rules:
- Routes call these functions only — no OpenCV in routes.
- Does NOT touch enrollment_service or detection_service state.
- Camera opened and closed exclusively inside this module.
"""

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.core.camera import Camera
from app.core.detector import FaceDetector
from app.core.image_utils import apply_clahe, to_grayscale
from app.core.embedding import extract_embedding
from app.core.matcher import find_best_match
from app.db import crud

_detector = FaceDetector()

MAX_FACES     = 3
FONT          = cv2.FONT_HERSHEY_SIMPLEX
COLOR_MATCH   = (0, 255, 0)
COLOR_UNKNOWN = (0, 0, 255)


def run_recognition_loop(db: Session, device_index: int = 0) -> dict:
    """
    Start the live face recognition loop.

    For every frame:
        1. Capture BGR frame.
        2. Grayscale + CLAHE.
        3. Detect up to MAX_FACES faces.
        4. For each face: crop → embed → match → draw overlay.
        5. Display annotated frame.
        6. Break on 'q'.
    """
    total_frames = 0
    last_results = []

    with Camera(device_index=device_index) as cam:
        while True:
            frame        = cam.read_frame()
            total_frames += 1

            gray         = to_grayscale(frame)
            enhanced     = apply_clahe(gray)
            faces        = _detector.detect(enhanced)[:MAX_FACES]
            db_embeddings = crud.get_all_embeddings(db)

            frame_results = []

            for box in faces:
                x, y, w, h = box
                if w < 60 or h < 60:
                    continue

                face_crop = cv2.resize(frame[y:y + h, x:x + w], (160, 160))

                try:
                    query_vector = extract_embedding(face_crop)
                except ValueError:
                    _draw_unknown_box(frame, box)
                    continue

                result = find_best_match(query_vector, db_embeddings)
                frame_results.append(result)

                if result["matched"]:
                    _draw_match_overlay(frame, box, result)
                else:
                    _draw_unknown_box(frame, box)

            last_results = frame_results

            cv2.putText(
                frame,
                f"Faces: {len(faces)}  |  Press 'q' to stop",
                (10, frame.shape[0] - 15),
                FONT, 0.5, (200, 200, 200), 1, cv2.LINE_AA,
            )

            cv2.imshow("Face Recognition — Press 'q' to quit", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    return {"total_frames": total_frames, "last_results": last_results}


def recognize_single_frame(db: Session, device_index: int = 0) -> list[dict]:
    """
    Capture ONE frame, run recognition, return results immediately.
    Used by POST /recognize for a single-shot API response.
    """
    with Camera(device_index=device_index) as cam:
        for _ in range(5):       # warm up — let exposure settle
            cam.read_frame()
        frame = cam.read_frame()

    gray          = to_grayscale(frame)
    enhanced      = apply_clahe(gray)
    faces         = _detector.detect(enhanced)[:MAX_FACES]

    if not faces:
        return []

    db_embeddings = crud.get_all_embeddings(db)
    results       = []

    for box in faces:
        x, y, w, h = box
        if w < 60 or h < 60:
            continue

        face_crop = cv2.resize(frame[y:y + h, x:x + w], (160, 160))

        try:
            query_vector = extract_embedding(face_crop)
        except ValueError:
            results.append({"matched": False, "message": "No Match Found", "confidence": 0.0})
            continue

        results.append(find_best_match(query_vector, db_embeddings))

    return results


# ── Drawing helpers ───────────────────────────────────────────────────────────

def _draw_match_overlay(frame: np.ndarray, box: tuple, result: dict) -> None:
    x, y, w, h = box
    cv2.rectangle(frame, (x, y), (x + w, y + h), COLOR_MATCH, 2)
    label = f"{result['name']}  |  {result['employee_id']}  |  {result['confidence']:.2f}"
    (tw, th), _ = cv2.getTextSize(label, FONT, 0.55, 1)
    cv2.rectangle(frame, (x, y - th - 12), (x + tw + 8, y), (0, 180, 0), -1)
    cv2.putText(frame, label, (x + 4, y - 5), FONT, 0.55, (0, 0, 0), 1, cv2.LINE_AA)


def _draw_unknown_box(frame: np.ndarray, box: tuple) -> None:
    x, y, w, h = box
    cv2.rectangle(frame, (x, y), (x + w, y + h), COLOR_UNKNOWN, 2)
    label = "Unknown"
    (tw, th), _ = cv2.getTextSize(label, FONT, 0.6, 1)
    cv2.rectangle(frame, (x, y - th - 12), (x + tw + 8, y), (0, 0, 200), -1)
    cv2.putText(frame, label, (x + 4, y - 5), FONT, 0.6, (255, 255, 255), 1, cv2.LINE_AA)