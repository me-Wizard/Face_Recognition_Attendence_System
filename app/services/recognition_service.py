#C:\Attencence_System\app\services\recognition_service.py

"""
app/services/recognition_service.py
-------------------------------------
Recognition orchestration service.

Owns the recognition camera loop and ties together:
    Camera → FaceDetector → CLAHE → embedding → DB fetch → matcher → attendance → overlay

Phase 5 additions:
    - Frame skipping (process every Nth frame only)
    - FPS tracking
    - Per-frame latency monitoring
    - Stable multi-face identity cache to reduce overlay flicker

Rules:
- Routes call these functions only — no OpenCV in routes.
- Does NOT touch enrollment_service or detection_service state.
- Camera opened and closed exclusively inside this module.
"""

import time

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

MAX_FACES      = 3
FONT           = cv2.FONT_HERSHEY_SIMPLEX
COLOR_MATCH    = (0, 255, 0)
COLOR_UNKNOWN  = (0, 0, 255)
COLOR_MARKED   = (255, 165, 0)
COLOR_SUCCESS  = (0, 200, 255)

# ── Performance config ────────────────────────────────────────────────────────

FRAME_SKIP       = 3    # process every Nth frame — skips 2 out of 3
FPS_WINDOW       = 30   # rolling window size for FPS average

# ── Module-level performance state ───────────────────────────────────────────

_perf = {
    "fps":              0.0,
    "avg_latency_ms":   0.0,
    "total_frames":     0,
    "processed_frames": 0,
    "latency_samples":  [],
}


def get_performance_stats() -> dict:
    """Return current performance metrics. Used by GET /system/status."""
    return {
        "fps":              round(_perf["fps"], 2),
        "avg_latency_ms":   round(_perf["avg_latency_ms"], 2),
        "total_frames":     _perf["total_frames"],
        "processed_frames": _perf["processed_frames"],
    }


def run_recognition_loop(db: Session, device_index: int = 0) -> dict:
    """
    Start the live face recognition + attendance loop.

    Phase 5 changes:
        - Only processes every FRAME_SKIP-th frame.
        - Tracks FPS using timestamps of last FPS_WINDOW frames.
        - Measures per-frame recognition latency.
        - Caches last known overlay per face box to reduce flicker.
    """
    _perf["total_frames"]     = 0
    _perf["processed_frames"] = 0
    _perf["latency_samples"]  = []

    last_results:    list       = []
    previously_seen: set[str]   = set()

    # Cache: stores last drawn overlay data per face position slot
    # key = face index (0,1,2), value = (match_result, att_result)
    overlay_cache: dict[int, tuple] = {}

    # FPS tracking
    frame_timestamps: list[float] = []

    # Prefetch DB embeddings once — refresh every 60 processed frames
    db_embeddings      = crud.get_all_embeddings(db)
    embed_refresh_counter = 0

    with Camera(device_index=device_index) as cam:
        while True:
            frame_start = time.perf_counter()
            frame       = cam.read_frame()

            _perf["total_frames"] += 1
            now = time.time()

            # ── FPS calculation ───────────────────────────────────────────────
            frame_timestamps.append(now)
            if len(frame_timestamps) > FPS_WINDOW:
                frame_timestamps.pop(0)
            if len(frame_timestamps) >= 2:
                elapsed = frame_timestamps[-1] - frame_timestamps[0]
                _perf["fps"] = (len(frame_timestamps) - 1) / elapsed if elapsed > 0 else 0.0

            # ── Frame skipping ────────────────────────────────────────────────
            if _perf["total_frames"] % FRAME_SKIP != 0:
                # Re-draw last known overlay on skipped frames and show
                _redraw_cached_overlay(frame, overlay_cache)
                _draw_hud(frame, len(overlay_cache))
                cv2.imshow("Face Attendance — Press 'q' to quit", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue

            # ── Processed frame ───────────────────────────────────────────────
            _perf["processed_frames"] += 1
            embed_refresh_counter     += 1

            if embed_refresh_counter >= 60:
                db_embeddings         = crud.get_all_embeddings(db)
                embed_refresh_counter = 0

            gray     = to_grayscale(frame)
            enhanced = apply_clahe(gray)
            faces    = _detector.detect(enhanced)[:MAX_FACES]

            frame_results:   list      = []
            seen_this_frame: set[str]  = set()
            new_cache:       dict      = {}

            for idx, box in enumerate(faces):
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

                    att_result = attendance_service.process_recognition(
                        db=db,
                        employee_id=employee_id,
                        user_id=match_result["user_id"],
                        name=match_result["name"],
                        confidence=match_result["confidence"],
                    )

                    frame_results.append({**match_result, "attendance": att_result})
                    _draw_attendance_overlay(frame, box, match_result, att_result)
                    new_cache[idx] = (box, match_result, att_result)

                else:
                    _draw_unknown_box(frame, box)
                    frame_results.append(match_result)

            # Update overlay cache with this frame's results
            overlay_cache = new_cache

            # Reset counters for users who left frame
            lost_users = previously_seen - seen_this_frame
            for eid in lost_users:
                attendance_service.reset_frame_counter_for(eid)

            previously_seen = seen_this_frame
            last_results    = frame_results

            # ── Latency tracking ──────────────────────────────────────────────
            latency_ms = (time.perf_counter() - frame_start) * 1000
            _perf["latency_samples"].append(latency_ms)
            if len(_perf["latency_samples"]) > FPS_WINDOW:
                _perf["latency_samples"].pop(0)
            _perf["avg_latency_ms"] = sum(_perf["latency_samples"]) / len(_perf["latency_samples"])

            _draw_hud(frame, len(faces))
            cv2.imshow("Face Attendance — Press 'q' to quit", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    return {"total_frames": _perf["total_frames"], "last_results": last_results}


def recognize_single_frame(db: Session, device_index: int = 0) -> list[dict]:
    """
    Capture ONE frame, run recognition, return results immediately.
    No attendance marking — single shot only.
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

def _draw_hud(frame: np.ndarray, face_count: int) -> None:
    """Bottom status bar: FPS + latency + face count."""
    fps_text = (
        f"FPS: {_perf['fps']:.1f}  |  "
        f"Latency: {_perf['avg_latency_ms']:.1f}ms  |  "
        f"Faces: {face_count}  |  Press 'q' to stop"
    )
    cv2.putText(
        frame, fps_text,
        (10, frame.shape[0] - 15),
        FONT, 0.45, (200, 200, 200), 1, cv2.LINE_AA,
    )


def _redraw_cached_overlay(frame: np.ndarray, cache: dict) -> None:
    """Re-draw last known overlays on skipped frames to prevent flicker."""
    for _, (box, match_result, att_result) in cache.items():
        _draw_attendance_overlay(frame, box, match_result, att_result)


def _draw_attendance_overlay(
    frame: np.ndarray,
    box: tuple,
    match_result: dict,
    att_result: dict,
) -> None:
    x, y, w, h = box
    att_status  = att_result.get("status", "recognizing")

    if att_status == "success":
        box_color = COLOR_SUCCESS
        bg_color  = (0, 160, 200)
    elif att_status in ("exists", "cooldown"):
        box_color = COLOR_MARKED
        bg_color  = (180, 110, 0)
    else:
        box_color = COLOR_MATCH
        bg_color  = (0, 160, 0)

    cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)

    line1 = (
        f"{match_result['name']}  |  "
        f"{match_result['employee_id']}  |  "
        f"{match_result['confidence']:.2f}"
    )
    line2 = att_result.get("message", "")

    (tw1, th1), _ = cv2.getTextSize(line1, FONT, 0.50, 1)
    (tw2, th2), _ = cv2.getTextSize(line2, FONT, 0.50, 1)

    bar_w = max(tw1, tw2) + 12
    bar_h = th1 + th2 + 20

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