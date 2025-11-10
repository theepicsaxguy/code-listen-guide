"""add_plugin_id_to_workflow_steps

Revision ID: ef5623bff87d
Revises: 20251110_add_user_settings
Create Date: 2025-11-10 20:00:19.186159+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef5623bff87d'
down_revision: Union[str, Sequence[str], None] = '20251110_add_user_settings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'workflow_steps',
        sa.Column('plugin_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_foreign_key(
        'fk_workflow_steps_plugin_id_tools_registry',
        'workflow_steps',
        'tools_registry',
        ['plugin_id'],
        ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_workflow_steps_plugin_id_tools_registry', 'workflow_steps', type_='foreignkey')
    op.drop_column('workflow_steps', 'plugin_id')
