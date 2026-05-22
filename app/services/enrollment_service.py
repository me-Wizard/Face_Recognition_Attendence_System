"""
app/services/enrollment_service.py
------------------------------------
Enrollment orchestration service.

Owns the enrollment camera loop and ties together:
    Camera → FaceDetector → quality checks → embedding → DB storage

Rules:
- Routes call enroll_user() only — no OpenCV in routes.
- This service does NOT touch detection_service state.
- Camera is opened and closed exclusively inside this function.
"""

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.core.camera import Camera
from app.core.detector import FaceDetector
from app.core.image_utils import apply_clahe, to_grayscale, draw_bounding_boxes
from app.core.embedding import extract_embedding
from app.core.quality import (
    is_blurry,
    has_single_face,
    is_face_large_enough,
    is_duplicate_embedding,
)
from app.db import crud

# How many good samples to collect before finishing enrollment
REQUIRED_SAMPLES = 5

# Detector is shared — instantiated once per process
_detector = FaceDetector()


def enroll_user(
    db: Session,
    name: str,
    employee_id: str,
    department: str,
    device_index: int = 0,
) -> dict:
    """
    Run the full enrollment pipeline for one person.

    Steps:
        1. Check employee_id is not already enrolled.
        2. Open webcam.
        3. Loop over frames:
            a. Grayscale + CLAHE preprocessing.
            b. Face detection — skip if not exactly 1 face.
            c. Quality checks — skip if blurry or face too small.
            d. Crop face, extract FaceNet embedding.
            e. Duplicate check — skip if too similar to existing samples.
            f. Accumulate sample; show live progress on-screen.
        4. After REQUIRED_SAMPLES collected (or user presses 'q'):
            - Insert user row into DB.
            - Bulk-insert all embeddings.
        5. Return a result dict.

    Args:
        db:          SQLAlchemy session (injected by FastAPI Depends).
        name:        Full name of the person.
        employee_id: Unique employee / student identifier.
        department:  Department or class label.
        device_index: Webcam index (default 0).

    Returns:
        dict with keys: success, employee_id, samples_collected, message.

    Raises:
        ValueError: If employee_id already exists in the database.
    """
    # ── Pre-flight: duplicate employee check ──────────────────────────────────
    existing = crud.get_user_by_employee_id(db, employee_id)
    if existing:
        raise ValueError(f"Employee ID '{employee_id}' is already enrolled.")

    collected_embeddings: list[list[float]] = []
    collected_crops: list[np.ndarray] = []

    with Camera(device_index=device_index) as cam:
        while len(collected_embeddings) < REQUIRED_SAMPLES:
            # ── 1. Capture frame ──────────────────────────────────────────────
            frame = cam.read_frame()

            # ── 2. Preprocess ─────────────────────────────────────────────────
            gray     = to_grayscale(frame)
            enhanced = apply_clahe(gray)

            # ── 3. Detect faces ───────────────────────────────────────────────
            faces = _detector.detect(enhanced)

            # ── 4. Quality gate: exactly one face ─────────────────────────────
            if not has_single_face(faces):
                _draw_enrollment_overlay(
                    frame,
                    collected=len(collected_embeddings),
                    status="Position ONE face in frame",
                    color=(0, 165, 255),   # orange
                )
                cv2.imshow("Enrollment — Press 'q' to cancel", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            box = faces[0]
            x, y, w, h = box

            # ── 5. Quality gate: face large enough ────────────────────────────
            if not is_face_large_enough(box):
                _draw_enrollment_overlay(
                    frame,
                    collected=len(collected_embeddings),
                    status="Move closer to the camera",
                    color=(0, 165, 255),
                )
                cv2.imshow("Enrollment — Press 'q' to cancel", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            # ── 6. Quality gate: sharpness ────────────────────────────────────
            face_gray = gray[y:y + h, x:x + w]
            if is_blurry(face_gray):
                _draw_enrollment_overlay(
                    frame,
                    collected=len(collected_embeddings),
                    status="Hold still — frame too blurry",
                    color=(0, 165, 255),
                )
                cv2.imshow("Enrollment — Press 'q' to cancel", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            # ── 7. Crop face for embedding ────────────────────────────────────
            face_crop = frame[y:y + h, x:x + w]
            face_crop = cv2.resize(face_crop, (160, 160))  # FaceNet input size

            # ── 8. Extract embedding ──────────────────────────────────────────
            try:
                vector = extract_embedding(face_crop)
            except ValueError:
                # DeepFace could not detect a face in the crop — skip frame
                _draw_enrollment_overlay(
                    frame,
                    collected=len(collected_embeddings),
                    status="Cannot extract embedding — adjust position",
                    color=(0, 0, 255),
                )
                cv2.imshow("Enrollment — Press 'q' to cancel", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            # ── 9. Duplicate guard ────────────────────────────────────────────
            if is_duplicate_embedding(vector, collected_embeddings):
                _draw_enrollment_overlay(
                    frame,
                    collected=len(collected_embeddings),
                    status="Too similar to previous sample — move slightly",
                    color=(0, 165, 255),
                )
                cv2.imshow("Enrollment — Press 'q' to cancel", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            # ── 10. Accept sample ─────────────────────────────────────────────
            collected_embeddings.append(vector)
            collected_crops.append(face_crop)

            # Draw bounding box on the accepted frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            _draw_enrollment_overlay(
                frame,
                collected=len(collected_embeddings),
                status=f"Sample {len(collected_embeddings)}/{REQUIRED_SAMPLES} captured!",
                color=(0, 255, 0),
            )
            cv2.imshow("Enrollment — Press 'q' to cancel", frame)

            # Show the accepted crop in a side window
            cv2.imshow(f"Sample {len(collected_embeddings)}", face_crop)

            if cv2.waitKey(300) & 0xFF == ord("q"):   # brief pause so user sees the capture
                break

    # ── Save to database if we have at least one sample ───────────────────────
    if not collected_embeddings:
        return {
            "success": False,
            "employee_id": employee_id,
            "samples_collected": 0,
            "message": "Enrollment cancelled — no valid samples collected.",
        }

    user = crud.create_user(db, name=name, employee_id=employee_id, department=department)
    crud.save_all_embeddings(db, user_id=user.id, vectors=collected_embeddings)

    return {
        "success": True,
        "employee_id": employee_id,
        "user_id": str(user.id),
        "name": name,
        "department": department,
        "samples_collected": len(collected_embeddings),
        "message": (
            f"Enrollment complete. {len(collected_embeddings)} embeddings stored."
            if len(collected_embeddings) == REQUIRED_SAMPLES
            else f"Partial enrollment: {len(collected_embeddings)}/{REQUIRED_SAMPLES} samples stored."
        ),
    }


# ── Internal helpers ──────────────────────────────────────────────────────────

def _draw_enrollment_overlay(
    frame: np.ndarray,
    collected: int,
    status: str,
    color: tuple[int, int, int],
) -> None:
    """Draw progress bar and status text on the enrollment window frame."""
    h, w = frame.shape[:2]
    font       = cv2.FONT_HERSHEY_SIMPLEX

    # Progress bar background
    bar_x, bar_y, bar_w, bar_h = 10, h - 50, w - 20, 20
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)

    # Filled progress
    filled = int(bar_w * (collected / REQUIRED_SAMPLES))
    if filled > 0:
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled, bar_y + bar_h), (0, 200, 0), -1)

    # Progress text
    cv2.putText(
        frame, f"Samples: {collected}/{REQUIRED_SAMPLES}",
        (bar_x, bar_y - 8),
        font, 0.55, (255, 255, 255), 1, cv2.LINE_AA,
    )

    # Status message
    cv2.putText(frame, status, (10, 35), font, 0.7, color, 2, cv2.LINE_AA)
