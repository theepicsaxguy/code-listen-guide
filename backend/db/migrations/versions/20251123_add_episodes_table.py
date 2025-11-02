"""add episodes table and estimated_episodes column

Revision ID: 20251123_add_episodes
Revises: 20251122_add_structured_tool_costs
Create Date: 2025-11-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20251123_add_episodes'
down_revision = '20251122_add_structured_tool_costs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add estimated_episodes column to jobs if not present
    with op.batch_alter_table('jobs') as batch_op:
        batch_op.add_column(sa.Column('estimated_episodes', sa.Integer()))

    op.create_table(
        'episodes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), index=True, nullable=False),
        sa.Column('episode_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('narrative_theme', sa.Text(), nullable=False),
        sa.Column('file_clusters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dependency_graph', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('architectural_boundary', sa.String(length=255), nullable=True),
        sa.Column('conversation_hooks', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_objectives', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('estimated_tokens', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('pending','planning','scripting','synthesizing','completed','failed', name='episodestatus'), nullable=True, server_default='pending'),
        sa.Column('dialogue_script', sa.Text(), nullable=True),
        sa.Column('audio_url', sa.String(length=500), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )
    op.create_index('ix_episodes_job_id', 'episodes', ['job_id'])
    op.create_index('ix_episodes_status', 'episodes', ['status'])


def downgrade() -> None:
    op.drop_index('ix_episodes_status', table_name='episodes')
    op.drop_index('ix_episodes_job_id', table_name='episodes')
    op.drop_table('episodes')

    with op.batch_alter_table('jobs') as batch_op:
        batch_op.drop_column('estimated_episodes')

    # Drop enum type explicitly (PostgreSQL)
    op.execute("DROP TYPE IF EXISTS episodestatus")
