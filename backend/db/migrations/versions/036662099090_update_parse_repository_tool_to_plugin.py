"""update_parse_repository_tool_to_plugin

Revision ID: 036662099090
Revises: ef5623bff87d
Create Date: 2025-11-10 23:28:25.247604+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '036662099090'
down_revision: Union[str, Sequence[str], None] = 'ef5623bff87d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update parse_repository tool to use new plugin module."""
    # Update existing parse_repository tool to point to new plugin location
    op.execute("""
        UPDATE tools_registry
        SET
            module_path = 'backend.plugins.repository_parser',
            function_name = 'parse_repository',
            description = 'Parse repository using chonkie pipeline. Returns structured metadata including file contents, functions, classes, imports, dependencies, languages, and frameworks.',
            updated_at = NOW()
        WHERE name = 'parse_repository'
    """)


def downgrade() -> None:
    """Revert parse_repository tool to old agent location."""
    # Revert to old location in analyzer_agent
    op.execute("""
        UPDATE tools_registry
        SET
            module_path = 'backend.agents.analyzer_agent',
            function_name = '_ai_parse_repository',
            description = 'Run the chonkie pipeline to analyse repository structure',
            updated_at = NOW()
        WHERE name = 'parse_repository'
    """)
