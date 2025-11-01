from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.db.base import Base
from backend.models.job import Job

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

    job = relationship(Job, foreign_keys=[job_id])
    revision = relationship("WorkflowRevision", foreign_keys=[revision_id])
    current_step = relationship("WorkflowStep")
