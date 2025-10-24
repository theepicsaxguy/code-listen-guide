from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20241025_add_workflow_checkpoints"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_checkpoints",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("workflow_id", sa.String(), nullable=False),
        sa.Column("step_id", sa.String(), nullable=False),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_workflow_checkpoints_workflow_id",
        "workflow_checkpoints",
        ["workflow_id"],
    )
    op.create_index(
        "ix_workflow_checkpoints_step_id",
        "workflow_checkpoints",
        ["step_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_workflow_checkpoints_step_id", table_name="workflow_checkpoints")
    op.drop_index("ix_workflow_checkpoints_workflow_id", table_name="workflow_checkpoints")
    op.drop_table("workflow_checkpoints")
