from alembic import op

from backend.db.session import Base
from backend.models import (  # noqa: F401  # pylint: disable=unused-import
    chapter,
    deliverable,
    job,
    outline,
    payment,
    usage_log,
    user,
    workflow_checkpoint,
)

revision = "20241025_add_workflow_checkpoints"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
