"""
app/core/camera.py
------------------
Handles webcam initialization, frame capture, and release.
This module is the sole owner of the cv2.VideoCapture object.
No detection logic lives here — only hardware I/O.
"""

import cv2


class Camera:
    """
    Encapsulates webcam capture lifecycle.

    Usage:
        cam = Camera()
        cam.open()
        frame = cam.read_frame()
        cam.release()

    Or use as a context manager:
        with Camera() as cam:
            frame = cam.read_frame()
    """

    def __init__(self, device_index: int = 0):
        self.device_index = device_index
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        """Open the webcam. Raises RuntimeError if the device cannot be opened."""
        self._cap = cv2.VideoCapture(self.device_index)
        if not self._cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera at device index {self.device_index}. "
                "Ensure a webcam is connected and not used by another process."
            )

    def read_frame(self):
        """
        Read a single frame from the webcam.

        Returns:
            numpy.ndarray: BGR image frame.

        Raises:
            RuntimeError: If the camera is not open or frame cannot be read.
        """
        if self._cap is None or not self._cap.isOpened():
            raise RuntimeError("Camera is not open. Call open() first.")

        success, frame = self._cap.read()
        if not success or frame is None:
            raise RuntimeError("Failed to read frame from camera.")

        return frame

    def is_open(self) -> bool:
        """Return True if the camera is currently open."""
        return self._cap is not None and self._cap.isOpened()

    def release(self) -> None:
        """Release the webcam and destroy any OpenCV windows."""
        if self._cap and self._cap.isOpened():
            self._cap.release()
        cv2.destroyAllWindows()
        self._cap = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False  # Do not suppress exceptions
