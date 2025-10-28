"""Database session management and initialization utilities."""

import logging
from importlib import import_module
from typing import Generator

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

connect_args: dict[str, object] = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provide a scoped database session for FastAPI dependencies."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Run database migrations that can't be handled by create_all()."""
    inspector = inspect(engine)

    # Migration: Add is_admin column to users table
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'is_admin' not in columns:
            logger.info("Running migration: Adding is_admin column to users table")
            with engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE"
                ))
                conn.commit()
            logger.info("✓ Successfully added is_admin column")


def init_db() -> None:
    """Create database tables for the registered SQLAlchemy models."""

    module_name = "backend.models.workflow_checkpoint"

    try:
        import_module(module_name)
    except ImportError as exc:
        logger.debug(
            "Model import failed during init_db: %s", module_name, exc_info=exc
        )

    Base.metadata.create_all(bind=engine)

    # Run migrations after creating tables
    run_migrations()
