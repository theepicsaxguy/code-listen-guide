"""
Job model representing an audiobook generation job.

TODO: Implementation steps:
1. Define Job SQLAlchemy model with all fields
2. Add foreign key relationship to User
3. Add relationships to Chapter, Outline, Deliverable
4. Implement status update methods
5. Add progress tracking methods
6. Create cost calculation methods
7. Add validation for depth_tier values
8. Implement indexes for user_id, status, created_at
"""

from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, Text, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional

from backend.db.session import Base


class Job(Base):
    """
    Job model representing an audiobook generation request.

    TODO:
    - Implement all fields from database schema
    - Add status transition validation
    - Create progress update methods
    - Implement cost tracking
    - Add relationship to User, Chapter, Outline, Deliverable
    - Create helper methods for status checks
    """

    __tablename__ = "jobs"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    # Repository Info
    repo_url = Column(String(500), nullable=False)
    repo_name = Column(String(255), nullable=False)
    repo_owner = Column(String(255), nullable=False)
    git_ref = Column(String(255), default="main")
    repo_size_bytes = Column(BigInteger)
    file_count = Column(Integer)

    # Configuration
    depth_tier = Column(String(50), nullable=False)  # survey, standard, comprehensive
    estimated_duration_minutes = Column(Integer)
    estimated_chapters = Column(Integer)

    # Processing Status
    status = Column(String(50), default="pending", index=True)
    # pending, analyzing, scripting, synthesizing, post_processing, completed, failed
    current_stage = Column(String(100))
    progress_percentage = Column(DECIMAL(5, 2), default=0.00)
    error_message = Column(Text)

    # Costs and Pricing
    price_paid_cents = Column(Integer)
    llm_cost_cents = Column(Integer)
    tts_cost_cents = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Metadata (flexible JSON field)
    metadata = Column(JSONB, default={})

    # Relationships
    # TODO: Add relationships
    # user = relationship("User", back_populates="jobs")
    # chapters = relationship("Chapter", back_populates="job", cascade="all, delete-orphan")
    # outline = relationship("Outline", back_populates="job", uselist=False)
    # deliverables = relationship("Deliverable", back_populates="job", cascade="all, delete-orphan")
    # payments = relationship("Payment", back_populates="job")

    def __repr__(self):
        return f"<Job {self.id} - {self.repo_name} ({self.status})>"

    # TODO: Implement methods
    # def update_status(self, status: str, stage: Optional[str] = None):
    #     """Update job status and optionally current stage."""
    #     pass
    #
    # def update_progress(self, percentage: float):
    #     """Update progress percentage (0-100)."""
    #     pass
    #
    # def mark_failed(self, error_message: str):
    #     """Mark job as failed with error message."""
    #     pass
    #
    # def mark_completed(self):
    #     """Mark job as completed."""
    #     pass
    #
    # def calculate_total_cost(self) -> int:
    #     """Calculate total cost in cents."""
    #     pass
    #
    # def is_processing(self) -> bool:
    #     """Check if job is currently being processed."""
    #     pass
