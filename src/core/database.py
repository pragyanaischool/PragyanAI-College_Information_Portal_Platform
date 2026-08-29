"""
src/core/database.py

Relational database engine, declarative Base, and session lifecycle management
for the PragyanAI College Intelligence Hub.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.core.config import settings

# -----------------------------------------------------------------------------
# 1. Engine Configuration
# -----------------------------------------------------------------------------
db_url = settings.DATABASE_URL

if "sqlite" in db_url:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool if ":memory:" in db_url else None,
        echo=False,
    )
else:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )

# -----------------------------------------------------------------------------
# 2. Session Factory & Declarative Base
# -----------------------------------------------------------------------------
# expire_on_commit=False prevents attributes from expiring after commit/close
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


# -----------------------------------------------------------------------------
# 3. Context Managers & Dependency Utilities
# -----------------------------------------------------------------------------
@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager for transactional database operations with auto-rollback."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI/Streamlit generator dependency providing a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Creates all database tables defined across SQLAlchemy models."""
    import src.db.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def check_db_health() -> bool:
    """Performs a lightweight query check to verify database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
