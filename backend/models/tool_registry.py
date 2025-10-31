from sqlalchemy import Column, String, Text, DateTime, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.db.base import Base
import uuid
from datetime import datetime

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
