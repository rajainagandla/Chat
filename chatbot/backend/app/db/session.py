"""Database session management using SQLAlchemy."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings
from .base_class import Base

# Use the configured database URL (PostgreSQL by default), SQLite for dev/tests.
DATABASE_URL = settings.database_url

# Ensure the data directory exists (SQLite needs the folder present).
Path("./data").mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables."""
    from . import models  # noqa: F401  (register models)

    Base.metadata.create_all(bind=engine)
