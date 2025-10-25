"""
Chapter model representing individual audiobook chapters.

All fields are defined and the model is ready to use.
Relationships and helper methods are commented out - uncomment when needed.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from backend.db.session import Base


class Chapter(Base):
    """
    Chapter model representing a single chapter in an audiobook.

    All fields are implemented. Uncomment relationships when Job model is active.
    """

    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint("job_id", "chapter_number", name="uq_job_chapter"),
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True)

    # Chapter Info
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Content Coverage
    files_covered = Column(ARRAY(Text))  # Array of file paths
    topics_covered = Column(ARRAY(Text))  # Array of topic names

    # Processing
    status = Column(String(50), default="pending", index=True)
    # pending, scripting, synthesizing, completed, failed
    script_text = Column(Text)

    # Audio
    audio_url = Column(String(1000))
    audio_duration_seconds = Column(Integer)
    audio_file_size_bytes = Column(BigInteger)

    # Timestamps
    start_timestamp_ms = Column(Integer)  # Position in full audiobook
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships (uncomment when Job model is active)
    # job = relationship("Job", back_populates="chapters")

    def __repr__(self):
        return f"<Chapter {self.chapter_number}: {self.title} ({self.status})>"

    # Helper methods (uncomment and implement as needed)
    # def update_status(self, status: str):
    #     """Update chapter processing status."""
    #     pass
    #
    # def save_script(self, script: str):
    #     """Save generated script for this chapter."""
    #     pass
    #
    # def save_audio(self, url: str, duration_seconds: int, file_size: int):
    #     """Save audio file information."""
    #     pass
    #
    # def mark_completed(self):
    #     """Mark chapter as completed."""
    #     pass
