"""
UsageLog model for tracking API usage and costs.

All fields are defined and the model is ready to use.
Relationships and helper methods are commented out - uncomment when needed.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from backend.db.base import Base


class UsageLog(Base):
    """
    UsageLog model for tracking API usage and costs.

    All fields are implemented. Uncomment relationships when User and Job models are active.
    """

    __tablename__ = "usage_logs"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))

    # Event Info
    event_type = Column(String(100), nullable=False)
    # repo_analyzed, script_generated, audio_synthesized, etc.

    # Usage Metrics
    tokens_used = Column(Integer)
    audio_seconds_generated = Column(Integer)

    # Cost Tracking
    cost_cents = Column(Integer)
    provider = Column(String(50))  # anthropic, openai, openai_tts, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships (uncomment when User and Job models are active)
    # user = relationship("User", back_populates="usage_logs")
    # job = relationship("Job", back_populates="usage_logs")

    def __repr__(self):
        return f"<UsageLog {self.event_type} - {self.provider} (${self.cost_cents/100:.2f})>"

    # Helper methods (uncomment and implement as needed)
    # @classmethod
    # def log_event(cls, user_id, job_id, event_type, provider, cost_cents, **kwargs):
    #     """Create usage log entry."""
    #     pass
    #
    # @classmethod
    # def get_user_usage(cls, user_id, start_date=None, end_date=None):
    #     """Get usage statistics for a user."""
    #     pass
