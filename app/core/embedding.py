"""
app/core/embedding.py
---------------------
Face embedding extraction using DeepFace + FaceNet.

Responsibilities:
- Accept a cropped BGR face image (numpy array).
- Run DeepFace.represent() with the FaceNet model.
- Return a normalised 128-D float list.

This module has NO knowledge of the database or the enrollment flow.
It is a pure image-in → vector-out function.
"""

import numpy as np

# DeepFace is imported lazily inside the function so the module can be
# imported at startup without triggering the full TensorFlow load.
# The first actual call will take a few seconds while the model loads;
# subsequent calls are fast.

MODEL_NAME = "Facenet"          # 128-D embeddings
DETECTOR_BACKEND = "opencv"     # use the same OpenCV backend already in use


def extract_embedding(face_bgr: np.ndarray) -> list[float]:
    """
    Generate a FaceNet embedding from a cropped face image.

    Args:
        face_bgr: BGR numpy array of a single face crop.
                  Recommended minimum size: 160×160.
                  The image must contain exactly ONE face.

    Returns:
        List of 128 floats — the L2-normalised FaceNet embedding vector.

    Raises:
        ValueError: If DeepFace cannot find a face in the crop or
                    if the image is too small / too blurry.
    """
    from deepface import DeepFace  # lazy import — avoids TF load at startup

    try:
        result = DeepFace.represent(
            img_path=face_bgr,          # accepts numpy array directly
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,     # raise if no face found
            align=True,                 # apply facial landmark alignment
        )
    except Exception as exc:
        raise ValueError(f"DeepFace failed to extract embedding: {exc}") from exc

    # DeepFace.represent() returns a list of dicts; take the first result
    raw_vector: list[float] = result[0]["embedding"]

    # L2-normalise so cosine similarity == dot product at recognition time
    vec = np.array(raw_vector, dtype=np.float32)
    norm = np.linalg.norm(vec)
    if norm == 0:
        raise ValueError("Embedding vector has zero norm — invalid face crop.")

    normalised = (vec / norm).tolist()
    return normalised
