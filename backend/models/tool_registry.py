"""SQLAlchemy model for registered tools/plugins available to agents."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from backend.db.base import Base

class ToolRegistry(Base):
    __tablename__ = "tools_registry"
    __table_args__ = (
        UniqueConstraint("name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    module_path = Column(String(500), nullable=False)
    function_name = Column(String(255), nullable=False)
    description = Column(Text)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
