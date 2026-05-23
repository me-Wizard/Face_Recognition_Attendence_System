#C:\Attencence_System\app\services\recognition_service.py

"""
app/services/recognition_service.py
-------------------------------------
Recognition orchestration service.

Owns the recognition camera loop and ties together:
    Camera → FaceDetector → CLAHE → embedding → DB fetch → matcher → attendance → overlay

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
from app.services import attendance_service

_detector = FaceDetector()

MAX_FACES     = 3
FONT          = cv2.FONT_HERSHEY_SIMPLEX
COLOR_MATCH   = (0, 255, 0)
COLOR_UNKNOWN = (0, 0, 255)
COLOR_MARKED  = (255, 165, 0)   # orange — already present
COLOR_SUCCESS = (0, 200, 255)   # cyan — just marked


def run_recognition_loop(db: Session, device_index: int = 0) -> dict:
    """
    Start the live face recognition + attendance loop.

    For every frame:
        1. Capture BGR frame.
        2. Grayscale + CLAHE.
        3. Detect up to MAX_FACES faces.
        4. For each face: crop → embed → match → attendance → overlay.
        5. Display annotated frame.
        6. Break on 'q'.
    """
    total_frames  = 0
    last_results  = []

    # Track which employee_ids were seen this frame
    # to reset counters for those NOT seen
    previously_seen: set[str] = set()

    with Camera(device_index=device_index) as cam:
        while True:
            frame         = cam.read_frame()
            total_frames += 1

            gray          = to_grayscale(frame)
            enhanced      = apply_clahe(gray)
            faces         = _detector.detect(enhanced)[:MAX_FACES]
            db_embeddings = crud.get_all_embeddings(db)

            frame_results  = []
            seen_this_frame: set[str] = set()

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

                match_result = find_best_match(query_vector, db_embeddings)

                if match_result["matched"]:
                    employee_id = match_result["employee_id"]
                    seen_this_frame.add(employee_id)

                    # ── Attendance processing ─────────────────────────────────
                    att_result = attendance_service.process_recognition(
                        db=db,
                        employee_id=employee_id,
                        user_id=match_result["user_id"],
                        name=match_result["name"],
                        confidence=match_result["confidence"],
                    )

                    frame_results.append({**match_result, "attendance": att_result})
                    _draw_attendance_overlay(frame, box, match_result, att_result)

                else:
                    _draw_unknown_box(frame, box)
                    frame_results.append(match_result)

            # Reset frame counters for users not seen this frame
            lost_users = previously_seen - seen_this_frame
            for eid in lost_users:
                attendance_service.reset_frame_counter_for(eid)

            previously_seen = seen_this_frame
            last_results    = frame_results

            cv2.putText(
                frame,
                f"Faces: {len(faces)}  |  Press 'q' to stop",
                (10, frame.shape[0] - 15),
                FONT, 0.5, (200, 200, 200), 1, cv2.LINE_AA,
            )

            cv2.imshow("Face Attendance — Press 'q' to quit", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    return {"total_frames": total_frames, "last_results": last_results}


def recognize_single_frame(db: Session, device_index: int = 0) -> list[dict]:
    """
    Capture ONE frame, run recognition, return results immediately.
    Used by POST /recognize — no attendance marking on single shot.
    """
    with Camera(device_index=device_index) as cam:
        for _ in range(5):
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

def _draw_attendance_overlay(
    frame: np.ndarray,
    box: tuple,
    match_result: dict,
    att_result: dict,
) -> None:
    """
    Draw face box + two-line overlay based on attendance status.

    Line 1: Name | Employee ID | Confidence
    Line 2: Attendance status message
    """
    x, y, w, h = box
    att_status  = att_result.get("status", "recognizing")

    # Pick box color based on attendance outcome
    if att_status == "success":
        box_color  = COLOR_SUCCESS
        bg_color   = (0, 160, 200)
    elif att_status == "exists":
        box_color  = COLOR_MARKED
        bg_color   = (180, 110, 0)
    elif att_status == "cooldown":
        box_color  = COLOR_MARKED
        bg_color   = (180, 110, 0)
    else:
        # recognizing — still accumulating frames
        box_color  = COLOR_MATCH
        bg_color   = (0, 160, 0)

    cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)

    # Line 1: identity
    line1 = (
        f"{match_result['name']}  |  "
        f"{match_result['employee_id']}  |  "
        f"{match_result['confidence']:.2f}"
    )
    (tw1, th1), _ = cv2.getTextSize(line1, FONT, 0.50, 1)

    # Line 2: attendance status
    line2 = att_result.get("message", "")
    (tw2, th2), _ = cv2.getTextSize(line2, FONT, 0.50, 1)

    bar_w  = max(tw1, tw2) + 12
    bar_h  = th1 + th2 + 20      # padding between lines

    cv2.rectangle(frame, (x, y - bar_h - 4), (x + bar_w, y), bg_color, -1)
    cv2.putText(frame, line1, (x + 4, y - th2 - 12), FONT, 0.50, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, line2, (x + 4, y - 4),         FONT, 0.50, (255, 255, 255), 1, cv2.LINE_AA)


def _draw_unknown_box(frame: np.ndarray, box: tuple) -> None:
    x, y, w, h = box
    cv2.rectangle(frame, (x, y), (x + w, y + h), COLOR_UNKNOWN, 2)
    label = "Unknown"
    (tw, th), _ = cv2.getTextSize(label, FONT, 0.6, 1)
    cv2.rectangle(frame, (x, y - th - 12), (x + tw + 8, y), (0, 0, 200), -1)
    cv2.putText(frame, label, (x + 4, y - 5), FONT, 0.6, (255, 255, 255), 1, cv2.LINE_AA)