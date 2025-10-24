"""
Outline model for storing chapter structure before processing.

TODO: Implementation steps:
1. Define Outline SQLAlchemy model
2. Add foreign key relationship to Job
3. Store outline data as JSONB
4. Implement approval workflow
5. Add user modification tracking
6. Create validation methods for outline structure
"""

from sqlalchemy import Column, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from backend.db.session import Base


class Outline(Base):
    """
    Outline model storing the approved chapter structure for a job.

    TODO:
    - Implement all fields from database schema
    - Add JSONB field for outline data
    - Create approval workflow methods
    - Track user modifications
    - Add validation for outline structure
    - Implement relationship to Job
    """

    __tablename__ = "outlines"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)

    # Outline Data
    outline_data = Column(JSONB, nullable=False)  # Full chapter structure
    user_approved = Column(Boolean, default=False)
    user_modifications = Column(JSONB)  # Track what user changed

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))

    # Relationships
    # TODO: Add relationships
    # job = relationship("Job", back_populates="outline")

    def __repr__(self):
        return f"<Outline for Job {self.job_id} - Approved: {self.user_approved}>"

    # TODO: Implement methods
    # def approve(self):
    #     """Mark outline as approved by user."""
    #     pass
    #
    # def update_outline(self, new_outline_data: dict, modifications: dict):
    #     """Update outline with user modifications."""
    #     pass
    #
    # def get_chapter_count(self) -> int:
    #     """Get number of chapters in outline."""
    #     pass
    #
    # def validate_structure(self) -> bool:
    #     """Validate outline JSON structure."""
    #     pass
