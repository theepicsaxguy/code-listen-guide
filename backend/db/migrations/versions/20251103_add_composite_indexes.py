"""Add composite indexes for common query patterns.

Revision ID: 20251103_add_composite_indexes
Revises: 20251103_add_passkeys
Create Date: 2025-11-03

This migration adds composite indexes to optimize common query patterns:
- chapters(job_id, status) - frequently filtered together
- deliverables(job_id, file_type) - frequently filtered together  
- jobs(user_id, status) - frequently filtered together
- episodes(job_id, status) - frequently filtered together
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251103_add_composite_indexes'
down_revision = '20251103_add_passkeys'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create composite indexes for performance optimization."""
    # Composite index for chapters filtered by job_id and status
    op.create_index(
        'ix_chapters_job_status',
        'chapters',
        ['job_id', 'status'],
        unique=False
    )
    
    # Composite index for deliverables filtered by job_id and file_type
    op.create_index(
        'ix_deliverables_job_type',
        'deliverables',
        ['job_id', 'file_type'],
        unique=False
    )
    
    # Composite index for jobs filtered by user_id and status
    op.create_index(
        'ix_jobs_user_status',
        'jobs',
        ['user_id', 'status'],
        unique=False
    )
    
    # Composite index for episodes filtered by job_id and status
    op.create_index(
        'ix_episodes_job_status',
        'episodes',
        ['job_id', 'status'],
        unique=False
    )


def downgrade() -> None:
    """Remove composite indexes."""
    op.drop_index('ix_episodes_job_status', table_name='episodes')
    op.drop_index('ix_jobs_user_status', table_name='jobs')
    op.drop_index('ix_deliverables_job_type', table_name='deliverables')
    op.drop_index('ix_chapters_job_status', table_name='chapters')

