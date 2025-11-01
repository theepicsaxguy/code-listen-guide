"""SQLAlchemy model describing registered agents available to workflows."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.db.base import Base

class AgentRegistry(Base):
    __tablename__ = "agents_registry"
    __table_args__ = (
        UniqueConstraint("name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    module_path = Column(String(500), nullable=False)
    factory_function = Column(String(255), nullable=False)
    description = Column(Text)
    config_schema = Column(JSON)
    tools = Column(JSON, default=list, server_default=text("'[]'::jsonb"), nullable=False)
    account_acl = Column(JSON, default=list, server_default=text("'[]'::jsonb"), nullable=False)
    quota_limits = Column(JSON, default=list, server_default=text("'[]'::jsonb"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    steps = relationship(
        "WorkflowStep",
        back_populates="agent",
    )
