from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.db.base import Base

class WorkflowRevision(Base):
    __tablename__ = "workflow_revisions"
    __table_args__ = (
        UniqueConstraint("workflow_definition_id", "version"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_definition_id = Column(UUID(as_uuid=True), ForeignKey("workflow_definitions.id"), nullable=False)
    version = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False)
    revision_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime)

    workflow_definition = relationship(
        "WorkflowDefinition",
        back_populates="revisions",
    )
    steps = relationship(
        "WorkflowStep",
        back_populates="revision",
        cascade="all, delete-orphan",
        order_by="WorkflowStep.step_order",
    )
