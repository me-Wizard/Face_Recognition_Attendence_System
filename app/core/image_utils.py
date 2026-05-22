"""
app/core/image_utils.py
-----------------------
Pure image-processing utilities.

Each function is stateless — input in, output out.
No camera access, no detection logic, no side effects.

Functions:
    to_grayscale()      – Convert BGR frame to grayscale.
    apply_clahe()       – Brightness/contrast normalisation via CLAHE.
    draw_bounding_boxes() – Draw boxes + status label on the BGR frame.
    crop_and_resize()   – Extract and resize a face region.
    show_cropped_faces()  – Display cropped faces in a separate window.
"""

import cv2
import numpy as np

# CLAHE instance — created once, reused every frame
_clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Output size for cropped / zoomed face windows
FACE_CROP_SIZE = (200, 200)

# Visual style constants
BOX_COLOR        = (0, 255, 0)      # Green bounding box
TEXT_COLOR_OK    = (0, 255, 0)      # Green text when face detected
TEXT_COLOR_NONE  = (0, 0, 255)      # Red text when no face detected
FONT             = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE       = 0.75
FONT_THICKNESS   = 2
BOX_THICKNESS    = 2


def to_grayscale(frame: np.ndarray) -> np.ndarray:
    """
    Convert a BGR frame to single-channel grayscale.

    Args:
        frame: H×W×3 BGR numpy array from cv2.VideoCapture.

    Returns:
        H×W single-channel uint8 array.
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def apply_clahe(gray_frame: np.ndarray) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalisation).

    CLAHE divides the image into tiles and equalises each tile independently,
    which normalises local brightness variations caused by uneven lighting.
    This significantly improves Haar Cascade detection under poor or uneven light.

    Args:
        gray_frame: Single-channel grayscale frame.

    Returns:
        CLAHE-enhanced single-channel frame (same shape and dtype).
    """
    return _clahe.apply(gray_frame)


def draw_bounding_boxes(
    frame: np.ndarray,
    faces: list[tuple[int, int, int, int]],
) -> np.ndarray:
    """
    Draw bounding boxes and a status label directly on the BGR frame.

    The frame is modified in-place AND returned for convenience.

    Status text drawn:
        "Face Detected"    – one or more faces found (green)
        "No Face Detected" – no faces found (red)

    Args:
        frame: H×W×3 BGR frame (will be mutated in-place).
        faces: List of (x, y, w, h) bounding boxes from FaceDetector.detect().

    Returns:
        The annotated BGR frame (same object as input).
    """
    if faces:
        status_text  = "Face Detected"
        text_color   = TEXT_COLOR_OK
    else:
        status_text  = "No Face Detected"
        text_color   = TEXT_COLOR_NONE

    # Draw one rectangle per detected face
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), BOX_COLOR, BOX_THICKNESS)

        # Small label above each individual box showing face count index
        label = f"Face"
        cv2.putText(
            frame, label,
            (x, y - 8),
            FONT, 0.55, BOX_COLOR, 1, cv2.LINE_AA,
        )

    # Global status banner at top-left of frame
    cv2.putText(
        frame, status_text,
        (10, 35),
        FONT, FONT_SCALE, text_color, FONT_THICKNESS, cv2.LINE_AA,
    )

    # Face count sub-label
    count_text = f"Count: {len(faces)}"
    cv2.putText(
        frame, count_text,
        (10, 65),
        FONT, 0.55, (255, 255, 255), 1, cv2.LINE_AA,
    )

    return frame


def crop_and_resize(
    frame: np.ndarray,
    box: tuple[int, int, int, int],
    size: tuple[int, int] = FACE_CROP_SIZE,
) -> np.ndarray:
    """
    Crop a face region from the frame and resize to a fixed square.

    Args:
        frame: Full BGR frame.
        box:   (x, y, w, h) bounding box from the detector.
        size:  (width, height) output size. Defaults to FACE_CROP_SIZE (200×200).

    Returns:
        Resized BGR crop. Returns a black image of `size` if the crop is invalid.
    """
    x, y, w, h = box
    h_max, w_max = frame.shape[:2]

    # Clamp to valid frame boundaries
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w_max, x + w)
    y2 = min(h_max, y + h)

    crop = frame[y1:y2, x1:x2]

    if crop.size == 0:
        return np.zeros((size[1], size[0], 3), dtype=np.uint8)

    return cv2.resize(crop, size, interpolation=cv2.INTER_LINEAR)


def show_cropped_faces(
    frame: np.ndarray,
    faces: list[tuple[int, int, int, int]],
) -> None:
    """
    Display cropped and resized face windows alongside the main feed.

    Opens one window per detected face named "Face 1", "Face 2", etc.
    Closes all crop windows when no faces are present.

    Args:
        frame: Full BGR frame used for cropping.
        faces: List of (x, y, w, h) bounding boxes.
    """
    if not faces:
        # Destroy any leftover crop windows from the previous frame
        for i in range(1, 4):
            try:
                cv2.destroyWindow(f"Face {i}")
            except cv2.error:
                pass  # Window didn't exist — safe to ignore
        return

    for idx, box in enumerate(faces, start=1):
        crop = crop_and_resize(frame, box)
        cv2.imshow(f"Face {idx}", crop)
