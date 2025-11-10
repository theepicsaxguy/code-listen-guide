"""Add settings JSON column to users table.

Revision ID: 20251110_add_user_settings
Revises: 20251103_add_composite_indexes
Create Date: 2025-11-10

This migration adds a settings JSON column to the users table to store
user preferences and configuration data.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '20251110_add_user_settings'
down_revision = '20251103_add_composite_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add settings column to users table."""
    # Add settings column as JSON type (works with both PostgreSQL and SQLite)
    op.add_column('users', sa.Column('settings', JSON, nullable=True))


def downgrade() -> None:
    """Remove settings column from users table."""
    op.drop_column('users', 'settings')
