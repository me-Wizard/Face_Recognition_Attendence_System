"""
app/db/models.py
----------------
PLACEHOLDER — SQLAlchemy ORM models.

Future implementation will define:

    Person
        id          (UUID primary key)
        name        (str)
        student_id  (str, unique)
        embedding   (BLOB / JSON — serialised float32 vector)
        created_at  (datetime)

    AttendanceRecord
        id          (UUID primary key)
        person_id   (FK → Person.id)
        timestamp   (datetime)
        confidence  (float — matching score from FAISS)

TODO:
    - Define Person model.
    - Define AttendanceRecord model with foreign key.
    - Add __repr__ methods for debugging.
    - Register models with Base.metadata for Alembic autogenerate.
"""
