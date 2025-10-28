"""add is_admin to users

Revision ID: 20241028_add_is_admin
Revises: 20241025_add_workflow_checkpoints
Create Date: 2024-10-28 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241028_add_is_admin'
down_revision = '20241025_add_workflow_checkpoints'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove is_admin column from users table
    op.drop_column('users', 'is_admin')
