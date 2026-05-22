"""
app/core/quality.py
-------------------
Frame quality checks for enrollment sample selection.

Each function is stateless: frame/crop in → bool/score out.
No camera, no DB, no embedding logic here.

Checks:
    is_blurry()            — Laplacian variance sharpness test
    has_single_face()      — Exactly one face in the frame
    is_face_large_enough() — Face bounding box meets minimum size
    is_duplicate_frame()   — Cosine similarity guard against consecutive dupes
"""

import cv2
import numpy as np

# ── Thresholds (tune these for your lighting environment) ─────────────────────
BLUR_THRESHOLD        = 80.0    # Laplacian variance; lower = blurrier
MIN_FACE_WIDTH        = 80      # pixels
MIN_FACE_HEIGHT       = 80      # pixels
DUPLICATE_SIMILARITY  = 0.98    # cosine similarity above this = duplicate


def laplacian_variance(gray_frame: np.ndarray) -> float:
    """Return the variance of the Laplacian — higher means sharper."""
    return float(cv2.Laplacian(gray_frame, cv2.CV_64F).var())


def is_blurry(gray_frame: np.ndarray) -> bool:
    """
    Return True if the frame is too blurry to produce a reliable embedding.

    Args:
        gray_frame: Single-channel grayscale image (full frame or face crop).
    """
    return laplacian_variance(gray_frame) < BLUR_THRESHOLD


def has_single_face(faces: list) -> bool:
    """
    Return True only when exactly one face was detected.

    Args:
        faces: List of (x, y, w, h) tuples from FaceDetector.detect().
    """
    return len(faces) == 1


def is_face_large_enough(box: tuple[int, int, int, int]) -> bool:
    """
    Return True if the bounding box meets the minimum size requirement.

    Small faces (far from camera or partially cropped) produce
    poor-quality embeddings.

    Args:
        box: (x, y, w, h) bounding box tuple.
    """
    _, _, w, h = box
    return w >= MIN_FACE_WIDTH and h >= MIN_FACE_HEIGHT


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Return cosine similarity between two embedding vectors."""
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def is_duplicate_embedding(
    new_vector: list[float],
    existing_vectors: list[list[float]],
) -> bool:
    """
    Return True if new_vector is too similar to any already-collected sample.

    Prevents storing near-identical frames as separate training samples.

    Args:
        new_vector:       The newly extracted embedding.
        existing_vectors: All embeddings collected so far in this session.
    """
    for existing in existing_vectors:
        if cosine_similarity(new_vector, existing) >= DUPLICATE_SIMILARITY:
            return True
    return False
