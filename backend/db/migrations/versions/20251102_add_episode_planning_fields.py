"""add episode planning relationship and pacing fields

Revision ID: 20251102_add_episode_planning_fields
Revises: 20251123_add_episodes
Create Date: 2025-11-02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20251102_add_episode_planning_fields'
down_revision = '20251123_add_episodes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new JSONB planning / dependency fields to episodes table.

    Fields:
      - goals
      - dependency_inputs
      - dependency_outputs
      - depends_on
      - leads_to
      - estimated_duration_minutes
    """
    with op.batch_alter_table('episodes') as batch_op:
        batch_op.add_column(sa.Column('goals', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('dependency_inputs', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('dependency_outputs', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('depends_on', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('leads_to', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('episodes') as batch_op:
        batch_op.drop_column('estimated_duration_minutes')
        batch_op.drop_column('leads_to')
        batch_op.drop_column('depends_on')
        batch_op.drop_column('dependency_outputs')
        batch_op.drop_column('dependency_inputs')
        batch_op.drop_column('goals')
