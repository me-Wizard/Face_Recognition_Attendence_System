"""
app/core/detector.py
--------------------
Haar Cascade face detector.

Responsibilities:
- Load the Haar Cascade XML classifier once at startup.
- Accept a preprocessed grayscale frame and return face bounding boxes.
- No camera logic, no drawing, no CLAHE — detection only.
"""

import cv2
import numpy as np
from pathlib import Path


# Path to OpenCV's bundled Haar Cascade for frontal faces
_CASCADE_PATH = str(
    Path(cv2.__file__).parent / "data" / "haarcascade_frontalface_default.xml"
)

# Maximum number of faces to process per frame (keeps system stable)
MAX_FACES = 3


class FaceDetector:
    """
    Wraps the OpenCV Haar Cascade classifier.

    The classifier is loaded once when the instance is created.
    Call detect() on every preprocessed grayscale frame.
    """

    def __init__(self):
        self._classifier = cv2.CascadeClassifier(_CASCADE_PATH)
        if self._classifier.empty():
            raise RuntimeError(
                f"Failed to load Haar Cascade from: {_CASCADE_PATH}\n"
                "Ensure opencv-python is correctly installed."
            )

    def detect(self, gray_frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        """
        Detect faces in a preprocessed grayscale frame.

        Args:
            gray_frame: Single-channel (grayscale) numpy array, already
                        brightness-normalised via CLAHE.

        Returns:
            List of bounding boxes as (x, y, w, h) tuples.
            Returns at most MAX_FACES entries; empty list if none found.

        Detection parameters:
            scaleFactor  – 1.1  : image pyramid scale step (10 % reduction per level)
            minNeighbors – 6    : higher = fewer false positives
            minSize      – (60, 60) : ignore detections smaller than 60×60 px
        """
        faces = self._classifier.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        if len(faces) == 0:
            return []

        # Convert numpy array rows to plain tuples and cap at MAX_FACES
        return [tuple(box) for box in faces[:MAX_FACES]]
