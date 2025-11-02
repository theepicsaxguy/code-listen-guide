"""add_scope_selection_to_jobs

Revision ID: 20241102_scope_selection
Revises: 20251031_add_payment_metadata
Create Date: 2024-11-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20241102_scope_selection'
down_revision: Union[str, None] = '20251031_add_payment_metadata'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add scope selection fields to jobs table for podcast vision."""
    # Add new columns
    op.add_column('jobs', sa.Column('selected_files', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('jobs', sa.Column('excluded_patterns', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('jobs', sa.Column('primary_language', sa.String(length=50), nullable=True))
    op.add_column('jobs', sa.Column('estimated_total_tokens', sa.Integer(), nullable=True))
    op.add_column('jobs', sa.Column('user_approved_cost', sa.Integer(), server_default='0', nullable=True))


def downgrade() -> None:
    """Remove scope selection fields from jobs table."""
    op.drop_column('jobs', 'user_approved_cost')
    op.drop_column('jobs', 'estimated_total_tokens')
    op.drop_column('jobs', 'primary_language')
    op.drop_column('jobs', 'excluded_patterns')
    op.drop_column('jobs', 'selected_files')
