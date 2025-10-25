"""Add workflow checkpoint persistence."""

from alembic import op
import sqlalchemy as sa


revision = "20241025_add_workflow_checkpoints"
down_revision = "20241010_initial_schema"
branch_labels = None
depends_on = None


TABLE_NAME = "workflow_checkpoints"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("workflow_id", sa.String(), nullable=False),
        sa.Column("step_id", sa.String(), nullable=False),
        sa.Column("state", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_workflow_checkpoints_workflow_id",
        TABLE_NAME,
        ["workflow_id"],
    )
    op.create_index(
        "ix_workflow_checkpoints_step_id",
        TABLE_NAME,
        ["step_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_workflow_checkpoints_step_id", table_name=TABLE_NAME)
    op.drop_index("ix_workflow_checkpoints_workflow_id", table_name=TABLE_NAME)
    op.drop_table(TABLE_NAME)
