"""add_dependency_analysis_tools

Revision ID: 5af54534a844
Revises: 03e771c8c198
Create Date: 2025-11-10 23:31:55.406156+00:00

"""
from typing import Sequence, Union
import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5af54534a844'
down_revision: Union[str, Sequence[str], None] = '03e771c8c198'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add dependency analysis tools to registry."""
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

    # Insert dependency analysis tools
    op.bulk_insert(
        tools_table,
        [
            {
                'id': uuid.uuid4(),
                'name': 'analyze_dependencies',
                'stable_slug': 'analyze-dependencies',
                'semantic_version': '1.0.0',
                'module_path': 'backend.plugins.dependency_graph',
                'function_name': 'analyze_dependencies',
                'description': 'Build import/dependency graph for code files across multiple languages (Python, JavaScript, TypeScript, Go). Returns mapping of files to their dependencies.',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'repo_root': {
                            'type': 'string',
                            'description': 'Path to repository root directory',
                        },
                        'files': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'List of relative file paths to analyze',
                        },
                        'primary_language': {
                            'type': 'string',
                            'description': 'Primary language (python, javascript, typescript, go)',
                        },
                    },
                    'required': ['repo_root', 'files'],
                },
                'output_schema': {
                    'type': 'object',
                    'description': 'Dictionary mapping file paths to lists of their dependencies',
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
                'name': 'cluster_dependencies',
                'stable_slug': 'cluster-dependencies',
                'semantic_version': '1.0.0',
                'module_path': 'backend.plugins.dependency_graph',
                'function_name': 'cluster_dependencies',
                'description': 'Cluster files into connected components based on import relationships. Groups related files together for documentation or refactoring planning.',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'repo_root': {
                            'type': 'string',
                            'description': 'Path to repository root directory',
                        },
                        'files': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'List of relative file paths to analyze',
                        },
                        'primary_language': {
                            'type': 'string',
                            'description': 'Primary language',
                        },
                    },
                    'required': ['repo_root', 'files'],
                },
                'output_schema': {
                    'type': 'array',
                    'description': 'List of clusters, each containing related files',
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
                'name': 'identify_architectural_layers',
                'stable_slug': 'identify-architectural-layers',
                'semantic_version': '1.0.0',
                'module_path': 'backend.plugins.dependency_graph',
                'function_name': 'identify_architectural_layers',
                'description': 'Identify architectural layers (API, business logic, data access, etc.) from file paths using heuristics.',
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'repo_root': {
                            'type': 'string',
                            'description': 'Path to repository root directory',
                        },
                        'files': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'List of relative file paths to analyze',
                        },
                        'primary_language': {
                            'type': 'string',
                            'description': 'Primary language',
                        },
                    },
                    'required': ['repo_root', 'files'],
                },
                'output_schema': {
                    'type': 'object',
                    'description': 'Dictionary mapping layer names to their file clusters',
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
    """Remove dependency analysis tools from registry."""
    op.execute("""
        DELETE FROM tools_registry
        WHERE module_path = 'backend.plugins.dependency_graph'
        AND function_name IN ('analyze_dependencies', 'cluster_dependencies', 'identify_architectural_layers')
    """)
