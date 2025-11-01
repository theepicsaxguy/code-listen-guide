"""Database migration runner for production deployments."""

import logging
import sys

from backend.db.session import run_migrations as session_run_migrations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migrations() -> bool:
    """Execute database migrations using the shared session helpers."""

    logger.info("Running database migrations")
    try:
        session_run_migrations()
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("✗ Migration failed", exc_info=exc)
        return False

    logger.info("✓ Database is up to date")
    return True


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
