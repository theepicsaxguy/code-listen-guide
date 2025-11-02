"""Merge divergent heads (scope selection vs. episode planning).

Purpose:
    We had two concurrent heads:
      - 20241102_scope_selection (adds scope selection fields to jobs)
      - 20251102_add_episode_planning_fields (extends episodes planning fields)

    This merge migration creates a single linear history so future migrations
    can reference a single head. Both underlying schema changes had already
    been applied independently in development environments; therefore this
    migration performs no DDL. It exists solely to unify the revision graph.

Permanent Resolution Strategy:
    1. Always create new feature migrations off the latest single head.
    2. Avoid parallel development of migrations without coordination.
    3. If branching occurs again, prefer prompt merge with explicit comments.

Downgrade Policy:
    Downgrading past this merge would require selecting one branch lineage; we
    opt to NO-OP downgrade to prevent accidental branch re-creation.

Revision ID: 8327b05d4d00
Revises: 20241102_scope_selection, 20251102_add_episode_planning_fields
Create Date: 2025-11-02 15:51:03.271349+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8327b05d4d00'
down_revision: Union[str, Sequence[str], None] = ('20241102_scope_selection', '20251102_add_episode_planning_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:  # pragma: no cover
    """No-op: both parent heads already applied; unify revision lineage."""
    # Intentionally empty.
    return None


def downgrade() -> None:  # pragma: no cover
    """No-op: do not attempt to resurrect prior branch heads."""
    # Prevent accidental branch recreation.
    return None
