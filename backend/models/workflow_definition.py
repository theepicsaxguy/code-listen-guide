from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.db.base import Base

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"
    __table_args__ = (
        UniqueConstraint("name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    current_revision_id = Column(UUID(as_uuid=True), ForeignKey("workflow_revisions.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    revisions = relationship(
        "WorkflowRevision",
        back_populates="workflow_definition",
        cascade="all, delete-orphan",
        order_by="WorkflowRevision.version",
        foreign_keys="WorkflowRevision.workflow_definition_id",
    )
    current_revision = relationship(
        "WorkflowRevision",
        foreign_keys=[current_revision_id],
        post_update=True,
    )
