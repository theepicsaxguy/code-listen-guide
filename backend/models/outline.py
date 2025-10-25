"""
Outline model for storing chapter structure before processing.

All fields are defined and the model is ready to use.
Relationships and helper methods are commented out - uncomment when needed.
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

    All fields are implemented. Uncomment relationships when Job model is active.
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

    # Relationships (uncomment when Job model is active)
    # job = relationship("Job", back_populates="outline")

    def __repr__(self):
        return f"<Outline for Job {self.job_id} - Approved: {self.user_approved}>"

    # Helper methods (uncomment and implement as needed)
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
