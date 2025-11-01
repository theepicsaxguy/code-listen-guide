"""
Alembic migration to add workflow schema tables for dynamic workflow management.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

revision = '20251031_add_workflow_schema'
down_revision = '20251031_add_payment_metadata'
branch_labels = None
depends_on = None

def upgrade():
    # agents_registry (no dependencies)
    op.create_table(
        'agents_registry',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
        sa.Column('module_path', sa.String(500), nullable=False),
        sa.Column('factory_function', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('config_schema', postgresql.JSONB),
        sa.Column('tools', postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('account_acl', postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('quota_limits', postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.execute("UPDATE agents_registry SET tools = '[]'::jsonb WHERE tools IS NULL")
    op.execute("UPDATE agents_registry SET account_acl = '[]'::jsonb WHERE account_acl IS NULL")
    op.execute("UPDATE agents_registry SET quota_limits = '[]'::jsonb WHERE quota_limits IS NULL")

    # tools_registry (no dependencies)
    op.create_table(
        'tools_registry',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
        sa.Column('module_path', sa.String(500), nullable=False),
        sa.Column('function_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('input_schema', postgresql.JSONB),
        sa.Column('output_schema', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # workflow_definitions (without FK to workflow_revisions initially)
    op.create_table(
        'workflow_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('current_revision_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # workflow_revisions (depends on workflow_definitions)
    op.create_table(
        'workflow_revisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('workflow_definition_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_definitions.id'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_published', sa.Boolean(), default=False),
        sa.Column('revision_metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('published_at', sa.DateTime()),
        sa.UniqueConstraint('workflow_definition_id', 'version'),
    )

    # Now add the FK constraint from workflow_definitions to workflow_revisions
    op.create_foreign_key(
        'fk_workflow_definitions_current_revision',
        'workflow_definitions',
        'workflow_revisions',
        ['current_revision_id'],
        ['id']
    )

    # workflow_steps (depends on workflow_revisions and agents_registry)
    op.create_table(
        'workflow_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_revisions.id'), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(255), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agents_registry.id')),
        sa.Column('execution_mode', sa.String(50), nullable=False),
        sa.Column('input_mapping', postgresql.JSONB),
        sa.Column('output_mapping', postgresql.JSONB),
        sa.Column('checkpoint_enabled', sa.Boolean(), default=True),
        sa.Column('retry_policy', postgresql.JSONB),
        sa.Column('step_config', postgresql.JSONB),
        sa.UniqueConstraint('revision_id', 'step_order'),
    )

    # workflow_instances (depends on workflow_revisions and workflow_steps)
    op.create_table(
        'workflow_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_revisions.id'), nullable=False),
        sa.Column('current_step_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_steps.id')),
        sa.Column('instance_state', postgresql.JSONB),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('status', sa.String(50), nullable=False),
    )

def downgrade():
    op.drop_table('workflow_instances')
    op.drop_table('workflow_steps')
    
    # Drop FK constraint before dropping tables
    op.drop_constraint('fk_workflow_definitions_current_revision', 'workflow_definitions', type_='foreignkey')
    
    op.drop_table('workflow_revisions')
    op.drop_table('workflow_definitions')
    op.drop_table('tools_registry')
    op.drop_table('agents_registry')
