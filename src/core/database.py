"""
src/core/database.py

SQLAlchemy connection engine, thread-safe session manager, and health check
utilities for PragyanAI College Intelligence Hub. Supports SQLite and PostgreSQL.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.core.config import settings


def get_engine() -> Engine:
    """Initializes and returns the SQLAlchemy Engine based on DATABASE_URL."""
    db_url = settings.DATABASE_URL

    if db_url.startswith("sqlite"):
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=settings.DB_ECHO_SQL,
        )
    else:
        # PostgreSQL enterprise production settings
        return create_engine(
            db_url,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,
            echo=settings.DB_ECHO_SQL,
        )


# Singleton database engine and SessionLocal factory
engine: Engine = get_engine()

SessionLocal: sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Declarative Base for all relational ORM models
Base = declarative_base()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager for thread-safe database sessions with automatic commit/rollback.

    Usage:
        with get_db() as db:
            colleges = db.query(College).all()
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    """Dependency generator for API routes and Streamlit view injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initializes all database tables mapped to SQLAlchemy Base metadata."""
    from src.db.models import Base as AppBase  # Lazy import to prevent circular dependencies

    AppBase.metadata.create_all(bind=engine)


def check_db_health() -> bool:
    """Executes a lightweight query to verify active database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
