"""
Database migration runner for production deployments.

This script safely applies database migrations using SQLAlchemy directly,
without requiring Alembic configuration files.

Usage:
    python -m backend.db.migrate
"""

import sys
import logging
from sqlalchemy import create_engine, text, inspect
from backend.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_column_exists(engine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_is_admin_column(engine):
    """Add is_admin column to users table if it doesn't exist."""
    with engine.connect() as conn:
        if check_column_exists(engine, 'users', 'is_admin'):
            logger.info("✓ Column 'is_admin' already exists in users table")
            return False

        logger.info("Adding 'is_admin' column to users table...")
        conn.execute(text(
            "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        conn.commit()
        logger.info("✓ Successfully added 'is_admin' column")
        return True


def run_migrations():
    """Run all pending migrations."""
    try:
        settings = get_settings()
        logger.info(f"Connecting to database...")
        engine = create_engine(settings.database_url)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✓ Database connection successful")

        # Run migrations
        migrations_applied = []

        if add_is_admin_column(engine):
            migrations_applied.append("add_is_admin_column")

        if migrations_applied:
            logger.info(f"\n✓ Applied {len(migrations_applied)} migration(s):")
            for migration in migrations_applied:
                logger.info(f"  - {migration}")
        else:
            logger.info("\n✓ No new migrations to apply (database is up to date)")

        return True

    except Exception as e:
        logger.error(f"✗ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
