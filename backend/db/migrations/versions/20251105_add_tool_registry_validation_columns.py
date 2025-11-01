"""Add validation metadata columns to tools_registry."""

from alembic import op
import sqlalchemy as sa


revision = "20251105_add_tool_registry_validation_columns"
down_revision = "20251031_add_workflow_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tools_registry",
        sa.Column("signature_hash", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "tools_registry",
        sa.Column("input_schema_hash", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "tools_registry",
        sa.Column("output_schema_hash", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "tools_registry",
        sa.Column("last_validated_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "tools_registry",
        sa.Column("last_validation_error", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column("tools_registry", "last_validation_error")
    op.drop_column("tools_registry", "last_validated_at")
    op.drop_column("tools_registry", "output_schema_hash")
    op.drop_column("tools_registry", "input_schema_hash")
    op.drop_column("tools_registry", "signature_hash")
