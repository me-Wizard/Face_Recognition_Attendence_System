"""
app/core/matcher.py
-------------------
PLACEHOLDER — Face identity matching via FAISS.

Future implementation will:
- Build and manage a FAISS index of known face embeddings.
- Accept a query embedding from embedding.py.
- Return the closest matching identity (student ID / name) and
  a similarity score.
- Support adding new enrollments to the index at runtime.

TODO:
    - Implement FaissMatcher class.
    - add_face(embedding, identity_id) — register a new person.
    - find_match(embedding) -> (identity_id, score) — nearest-neighbour search.
    - Persist and reload index from disk between sessions.
"""
