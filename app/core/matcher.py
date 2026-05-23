"""
app/core/matcher.py
-------------------
Pure cosine similarity matching logic.
No DB logic. No FastAPI logic. No OpenCV. Pure numpy math only.
"""

import numpy as np

SIMILARITY_THRESHOLD = 0.65


def cosine_similarity(vec_a: list, vec_b: list) -> float:
    """
    Compute cosine similarity between two embedding vectors.

    Args:
        vec_a: First 128-D embedding vector.
        vec_b: Second 128-D embedding vector.

    Returns:
        Float in [-1.0, 1.0]. Closer to 1.0 means same person.
    """
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def find_best_match(
    query_vector: list,
    db_embeddings: list,
    threshold: float = SIMILARITY_THRESHOLD,
) -> dict:
    """
    Compare query embedding against all stored embeddings.
    Returns best match if above threshold, else Unknown.

    Args:
        query_vector:  128-D embedding from live face crop.
        db_embeddings: List of dicts from crud.get_all_embeddings().
                       Each dict has: user_id, employee_id, name, department, vector.
        threshold:     Minimum similarity to accept a match. Default 0.65.

    Returns:
        Matched:
            {"matched": True, "name": "...", "employee_id": "...",
             "department": "...", "confidence": 0.82}
        Unknown:
            {"matched": False, "message": "No Match Found", "confidence": 0.54}
    """
    if not db_embeddings:
        return {"matched": False, "message": "No Match Found", "confidence": 0.0}

    best_score = -1.0
    best_entry = None

    for entry in db_embeddings:
        score = cosine_similarity(query_vector, entry["vector"])
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_score >= threshold and best_entry is not None:
        return {
            "matched":     True,
            "user_id":     best_entry["user_id"],
            "name":        best_entry["name"],
            "employee_id": best_entry["employee_id"],
            "department":  best_entry["department"],
            "confidence":  round(best_score, 4),
        }

    return {
        "matched":    False,
        "message":    "No Match Found",
        "confidence": round(best_score, 4),
    }