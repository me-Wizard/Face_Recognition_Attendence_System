"""
app/core/embedding.py
---------------------
PLACEHOLDER — Face embedding extraction.

Future implementation will:
- Accept a cropped face image (200×200 BGR).
- Pass it through a lightweight embedding model
  (e.g., MobileFaceNet or a custom CNN).
- Return a 1-D float32 vector (embedding) representing the face.

This vector will be used by matcher.py for identity comparison.

TODO:
    - Load embedding model weights.
    - Implement extract(face_crop: np.ndarray) -> np.ndarray.
    - Normalise output vector to unit length for cosine similarity.
"""
