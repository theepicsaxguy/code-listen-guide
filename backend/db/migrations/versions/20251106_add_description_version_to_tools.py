"""Add description_version column to tools registry."""

from alembic import op
import sqlalchemy as sa


revision = "20251106_add_description_version_to_tools"
down_revision = "20251031_add_workflow_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tools_registry",
        sa.Column(
            "description_version",
            sa.String(length=64),
            nullable=False,
            server_default="1.0.0",
        ),
    )
    op.execute(
        "UPDATE tools_registry SET description_version = '1.0.0' WHERE description_version IS NULL"
    )


def downgrade() -> None:
    op.drop_column("tools_registry", "description_version")
