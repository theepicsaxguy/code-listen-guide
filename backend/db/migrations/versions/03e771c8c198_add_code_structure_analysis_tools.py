"""add_code_structure_analysis_tools

Revision ID: 03e771c8c198
Revises: 036662099090
Create Date: 2025-11-10 23:30:26.205532+00:00

"""
from typing import Sequence, Union
import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '03e771c8c198'
down_revision: Union[str, Sequence[str], None] = '036662099090'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add code structure analysis tools to registry."""
    # Create table reference
    tools_table = sa.table(
        'tools_registry',
        sa.column('id', postgresql.UUID(as_uuid=True)),
        sa.column('name', sa.String()),
        sa.column('stable_slug', sa.String()),
        sa.column('semantic_version', sa.String()),
        sa.column('module_path', sa.String()),
        sa.column('function_name', sa.String()),
        sa.column('description', sa.Text()),
        sa.column('input_schema', postgresql.JSONB()),
        sa.column('output_schema', postgresql.JSONB()),
        sa.column('schema_version', sa.Integer()),
        sa.column('owning_team', sa.String()),
        sa.column('authorization_scope', sa.String()),
        sa.column('approval_mode', sa.String()),
        sa.column('cost_profile', postgresql.JSONB()),
        sa.column('created_at', sa.DateTime()),
        sa.column('updated_at', sa.DateTime()),
    )

    # Insert analyze_code_structure tool
    op.bulk_insert(
        tools_table,
        [
            {
                'id': uuid.uuid4(),
                'name': 'analyze_code_structure',
                'stable_slug': 'analyze-code-structure',
                'semantic_version': '1.0.0',
                'module_path': 'backend.plugins.code_structure',
                'function_name': 'analyze_code_structure',
                'description': 'Analyze code structure using tree-sitter for deep metadata extraction. Returns functions, classes, imports, exports, call graphs, complexity metrics, and documentation.',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'file_path': {
                            'type': 'string',
                            'description': 'Path to the code file to analyze',
                        },
                        'content': {
                            'type': 'string',
                            'description': 'Optional file content (if not provided, will read from file_path)',
                        },
                    },
                    'required': ['file_path'],
                },
                'output_schema': {
                    'type': 'object',
                    'description': 'Structured code analysis with functions, classes, imports, metrics, and call graphs',
                },
                'schema_version': 1,
                'owning_team': 'core-platform',
                'authorization_scope': 'internal',
                'approval_mode': 'auto',
                'cost_profile': {'unit': 'call', 'estimated_cost_usd': 0.0},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
            {
                'id': uuid.uuid4(),
                'name': 'detect_file_language',
                'stable_slug': 'detect-file-language',
                'semantic_version': '1.0.0',
                'module_path': 'backend.plugins.code_structure',
                'function_name': 'detect_file_language',
                'description': 'Detect the programming language of a file based on extension and content analysis.',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'file_path': {
                            'type': 'string',
                            'description': 'Path to the code file',
                        },
                    },
                    'required': ['file_path'],
                },
                'output_schema': {
                    'type': 'string',
                    'description': 'Language identifier (e.g., python, javascript, typescript) or unknown',
                },
                'schema_version': 1,
                'owning_team': 'core-platform',
                'authorization_scope': 'internal',
                'approval_mode': 'auto',
                'cost_profile': {'unit': 'call', 'estimated_cost_usd': 0.0},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
        ]
    )


def downgrade() -> None:
    """Remove code structure analysis tools from registry."""
    op.execute("""
        DELETE FROM tools_registry
        WHERE module_path = 'backend.plugins.code_structure'
        AND function_name IN ('analyze_code_structure', 'detect_file_language')
    """)
