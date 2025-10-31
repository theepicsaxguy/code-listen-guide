from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.db.base import Base
import uuid
from datetime import datetime

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    __table_args__ = (
        UniqueConstraint("revision_id", "step_order"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_id = Column(UUID(as_uuid=True), ForeignKey("workflow_revisions.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    step_name = Column(String(255), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents_registry.id"))
    execution_mode = Column(String(50), nullable=False)
    input_mapping = Column(JSON)
    output_mapping = Column(JSON)
    checkpoint_enabled = Column(Boolean, default=True)
    retry_policy = Column(JSON)
    step_config = Column(JSON)

    # TODO: Add relationships after initial seeding
    # revision = relationship("WorkflowRevision", back_populates="steps")
    # agent = relationship("AgentRegistry")
