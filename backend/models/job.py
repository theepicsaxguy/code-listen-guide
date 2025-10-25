"""
Job model representing an audiobook generation job.

All fields are defined and the model is ready to use.
Relationships and helper methods are commented out - uncomment when needed.
"""

from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, Text, BigInteger, ForeignKey, JSON
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

    All fields are implemented. Uncomment relationships when other models are active.
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
    job_metadata = Column("metadata", JSONB().with_variant(JSON(), "sqlite"), default=dict)

    # Relationships (uncomment when other models are active)
    # user = relationship("User", back_populates="jobs")
    # chapters = relationship("Chapter", back_populates="job", cascade="all, delete-orphan")
    # outline = relationship("Outline", back_populates="job", uselist=False)
    # deliverables = relationship("Deliverable", back_populates="job", cascade="all, delete-orphan")
    # payments = relationship("Payment", back_populates="job")

    def __repr__(self):
        return f"<Job {self.id} - {self.repo_name} ({self.status})>"

    # Helper methods (uncomment and implement as needed)
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
