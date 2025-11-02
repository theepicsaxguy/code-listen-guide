"""Database session management and initialization utilities."""

import logging
import sys
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING, Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Connection, Inspector
from sqlalchemy.orm import Session, sessionmaker

from backend.config import get_settings
from backend.db.base import Base

if TYPE_CHECKING:
    from alembic.config import Config

logger = logging.getLogger(__name__)

# Ensure a dedicated stream handler for migration diagnostics so logs are always visible
if not any(getattr(h, 'name', '') == 'migration_stream' for h in logger.handlers):
    _handler = logging.StreamHandler(stream=sys.stdout)
    _handler.name = 'migration_stream'
    _handler.setLevel(logging.INFO)
    _handler.setFormatter(logging.Formatter('%(asctime)s | MIGRATION | %(levelname)s | %(message)s'))
    logger.addHandler(_handler)
    # Avoid duplicate propagation to root if root also logs
    logger.propagate = False

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
    
    logger.info("=" * 60)
    logger.info("Starting database migration check")
    logger.info("=" * 60)
    
    _apply_alembic_upgrades()
    
    with engine.begin() as connection:
        inspector = inspect(connection)
        _ensure_is_admin_column(connection, inspector)
    
    logger.info("=" * 60)
    logger.info("Database migration check completed successfully")
    logger.info("=" * 60)


def _apply_alembic_upgrades() -> None:
    """Apply all pending Alembic migrations to bring database to latest revision.
    
    This function follows Alembic best practices:
    1. Ensures alembic_version table exists with proper schema
    2. Automatically stamps database if tables exist but aren't tracked
    3. Runs all pending migrations using 'upgrade heads'
    """

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
    
    logger.info("Checking Alembic configuration...")
    
    # Ensure alembic_version table exists with correct schema
    _ensure_alembic_version_table()
    
    # Auto-stamp database if tables exist but Alembic isn't tracking them
    _auto_stamp_if_needed(alembic_cfg)

    # Pre-upgrade diagnostics
    _log_migration_diagnostics(alembic_cfg, phase="pre-upgrade")

    # Run all pending migrations to bring database to latest state
    logger.info("Running Alembic migration upgrade to 'heads'...")
    try:
        command.upgrade(alembic_cfg, "heads")
        logger.info("✓ All Alembic migrations applied successfully")
    except Exception as exc:
        logger.error("Failed to apply Alembic migrations: %s", exc, exc_info=True)
        raise

    # Post-upgrade diagnostics
    _log_migration_diagnostics(alembic_cfg, phase="post-upgrade")


def _ensure_alembic_version_table() -> None:
    """Ensure alembic_version table exists with sufficient VARCHAR size.
    
    Creates the table if missing, or recreates it if the version_num column
    is too small to hold modern Alembic revision IDs (which can be 40+ chars).
    """
    
    with engine.connect() as connection:
        inspector = inspect(connection)
        
        if "alembic_version" not in inspector.get_table_names():
            logger.info("Creating alembic_version table")
            connection.execute(
                text(
                    "CREATE TABLE alembic_version ("
                    "version_num VARCHAR(64) NOT NULL, "
                    "CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
                    ")"
                )
            )
            connection.commit()
            logger.info("✓ Created alembic_version table")
            return
        
        # Check if existing table has sufficient column size
        try:
            columns = inspector.get_columns("alembic_version")
            version_col = next((c for c in columns if c["name"] == "version_num"), None)
            
            if version_col and hasattr(version_col["type"], "length"):
                if version_col["type"].length and version_col["type"].length < 64:
                    logger.info(
                        "Upgrading alembic_version.version_num from VARCHAR(%s) to VARCHAR(64)",
                        version_col["type"].length
                    )
                    
                    # Preserve existing version if present
                    result = connection.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
                    existing_version = result.scalar()
                    
                    # Recreate table with larger column
                    connection.execute(text("DROP TABLE alembic_version"))
                    connection.execute(
                        text(
                            "CREATE TABLE alembic_version ("
                            "version_num VARCHAR(64) NOT NULL, "
                            "CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
                            ")"
                        )
                    )
                    
                    # Restore version if it exists and fits
                    if existing_version and len(existing_version) <= 64:
                        connection.execute(
                            text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
                            {"version": existing_version}
                        )
                    
                    connection.commit()
                    logger.info("✓ Upgraded alembic_version table schema")
        except Exception as exc:
            logger.debug("Could not check/upgrade alembic_version column size: %s", exc)


def _auto_stamp_if_needed(alembic_cfg: "Config") -> None:
    """Automatically stamp database to head if tables exist but aren't tracked.
    
    This handles the common scenario where:
    - Database was created manually or by SQLAlchemy Base.metadata.create_all()
    - Alembic migrations exist but database has never been stamped
    - Tables are present and match the current models
    
    In this case, we stamp the database to 'head' so future migrations work correctly.
    """
    
    from alembic import command
    
    with engine.connect() as connection:
        inspector = inspect(connection)
        existing_tables = inspector.get_table_names()
        
        # Skip if no tables exist (fresh database)
        if not existing_tables:
            return
        
        # Skip if alembic_version doesn't exist (will be created by first migration)
        if "alembic_version" not in existing_tables:
            return
            
        # Check if alembic_version is populated
        result = connection.execute(text("SELECT COUNT(*) FROM alembic_version"))
        has_version = result.scalar() > 0
        
        if not has_version:
            logger.warning(
                "⚠ Database has %d tables but no Alembic version tracked!",
                len(existing_tables)
            )
            logger.info("Auto-stamping database to 'head' revision...")
            try:
                command.stamp(alembic_cfg, "head")
                logger.info("✓ Database stamped to head revision")
            except Exception as exc:
                logger.warning("Failed to auto-stamp database: %s", exc)
                # Don't raise - upgrade might still work


def _log_migration_diagnostics(alembic_cfg: "Config", phase: str) -> None:
    """Output detailed migration diagnostics (current revision, heads, pending scripts).

    Args:
        alembic_cfg: Loaded Alembic Config
        phase: A label (e.g. 'pre-upgrade', 'post-upgrade')
    """
    try:
        from alembic.script import ScriptDirectory
    except ImportError:
        logger.debug("Alembic not available for diagnostics")
        return

    script_dir = ScriptDirectory.from_config(alembic_cfg)
    heads = script_dir.get_heads()  # list of head revision ids
    # Collect all revisions in linear order (may include branches)
    all_revs: list[str] = []
    try:
        for rev in script_dir.walk_revisions():  # walk from heads backwards
            all_revs.append(rev.revision)
    except Exception as exc:
        logger.debug("Failed walking revisions: %s", exc)

    # Current tracked revision(s)
    current_versions: list[str] = []
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version_num FROM alembic_version"))
        current_versions = [row[0] for row in result.fetchall()]

    # Determine if any head not present in current_versions (multi-head scenarios)
    missing_heads = [h for h in heads if h not in current_versions]

    logger.info("-" * 60)
    logger.info("Alembic diagnostics (%s)", phase)
    logger.info("Heads: %s", ', '.join(heads) if heads else '<none>')
    logger.info("Current versions: %s", ', '.join(current_versions) if current_versions else '<none>')
    if missing_heads:
        logger.info("Missing heads (will upgrade): %s", ', '.join(missing_heads))
    else:
        logger.info("All heads present in current versions")
    logger.info("Total migrations discovered: %d", len(all_revs))
    if phase == "pre-upgrade" and missing_heads:
        logger.info("Pending upgrade count: %d", len(missing_heads))
    logger.info("-" * 60)



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
