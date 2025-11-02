"""Database session management and initialization utilities."""

import logging
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Connection, Inspector
from sqlalchemy.orm import Session, sessionmaker

from backend.config import get_settings
from backend.db.base import Base

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


def get_db() -> Generator[Session, None, None]:
    """Provide a scoped database session for FastAPI dependencies."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Apply Alembic upgrades and manual schema migrations."""

    _apply_alembic_upgrades()
    with engine.begin() as connection:
        inspector = inspect(connection)
        _ensure_is_admin_column(connection, inspector)


def _apply_alembic_upgrades() -> None:
    """Apply the latest Alembic revision when configuration is available."""

    if find_spec("alembic") is None:
        logger.info("Alembic not installed; skipping migration upgrade")
        return

    from alembic import command
    from alembic.config import Config

    project_root = Path(__file__).resolve().parents[1]
    alembic_cfg_path = project_root / "alembic.ini"
    if not alembic_cfg_path.exists():
        logger.warning("Alembic configuration file not found at %s", alembic_cfg_path)
        return

    migrations_dir = project_root / "db" / "migrations"
    if not migrations_dir.exists():
        logger.warning("Alembic migrations directory not found at %s", migrations_dir)
        return

    alembic_cfg = Config(str(alembic_cfg_path))
    alembic_cfg.set_main_option("script_location", str(migrations_dir))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    logger.info("Applying Alembic migrations to latest revisions")
    try:
        command.upgrade(alembic_cfg, "heads")
    except Exception as exc:
        logger.warning("Failed to apply Alembic migrations: %s", exc)
        return

    logger.info("✓ Successfully applied Alembic migrations")


def _ensure_is_admin_column(connection: Connection, inspector: Inspector) -> None:
    """Add the users.is_admin column when the table predates migrations."""

    if "users" not in inspector.get_table_names():
        return

    columns = [column["name"] for column in inspector.get_columns("users")]
    if "is_admin" in columns:
        return

    logger.info("Running migration: Adding is_admin column to users table")
    connection.execute(
        text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE")
    )
    logger.info("✓ Successfully added is_admin column")


def init_db() -> None:
    """Create database tables for the registered SQLAlchemy models."""

    module_name = "backend.models"

    try:
        import_module(module_name)
    except ImportError as exc:
        logger.debug(
            "Model import failed during init_db: %s", module_name, exc_info=exc
        )

    run_migrations()
    Base.metadata.create_all(bind=engine)
