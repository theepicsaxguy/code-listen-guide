from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.db.base import Base
import uuid
from datetime import datetime

class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    revision_id = Column(UUID(as_uuid=True), ForeignKey("workflow_revisions.id"), nullable=False)
    current_step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id"))
    instance_state = Column(JSON)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String(50), nullable=False)

    # Relationships
    job = relationship("Job")
    revision = relationship("WorkflowRevision")
    current_step = relationship("WorkflowStep")
