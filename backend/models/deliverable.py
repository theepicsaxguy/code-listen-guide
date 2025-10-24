"""
Deliverable model for tracking generated files.

TODO: Implementation steps:
1. Define Deliverable SQLAlchemy model
2. Add foreign key relationship to Job
3. Track different file types (audio, scripts, cover, metadata)
4. Store S3 URLs and file metadata
5. Add file size tracking
6. Implement cleanup methods
"""

from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from backend.db.session import Base


class Deliverable(Base):
    """
    Deliverable model for tracking all generated files for a job.

    TODO:
    - Implement all fields from database schema
    - Track different file types
    - Store S3 URLs
    - Add relationship to Job
    - Implement file cleanup methods
    """

    __tablename__ = "deliverables"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True)

    # File Info
    file_type = Column(String(50), nullable=False)
    # full_audiobook, chapter_audio, scripts_zip, cover_image, metadata_json, outline_json, code_map_json
    file_url = Column(String(1000), nullable=False)
    file_size_bytes = Column(BigInteger)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    # TODO: Add relationships
    # job = relationship("Job", back_populates="deliverables")

    def __repr__(self):
        return f"<Deliverable {self.file_type} for Job {self.job_id}>"

    # TODO: Implement methods
    # def get_presigned_url(self, expiration: int = 3600) -> str:
    #     """Generate pre-signed S3 URL for download."""
    #     pass
    #
    # def delete_from_s3(self):
    #     """Delete file from S3 storage."""
    #     pass
