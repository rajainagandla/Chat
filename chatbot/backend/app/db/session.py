"""Database session management using SQLAlchemy."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite for development
DATABASE_URL = "sqlite:///./data/chatbot.db"

# Ensure the data directory exists (SQLite needs the folder present).
Path("./data").mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


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
