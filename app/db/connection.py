"""
app/db/connection.py
--------------------
Database engine, session factory, and FastAPI dependency.

Reads DATABASE_URL from environment (or .env file).
All other modules import `get_db` and `Base` from here.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/face_attendance",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # drop stale connections automatically
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields a DB session and closes it after the request.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all tables defined in models.py if they do not already exist.
    Called once at application startup from main.py.
    """
    from app.db import models  # noqa: F401 — import triggers table registration
    Base.metadata.create_all(bind=engine)
