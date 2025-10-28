"""
Pydantic schemas for Deliverable-related responses.

Deliverables represent output files from audiobook generation:
- Full audiobook MP3
- Individual chapter audio files
- Script text files
- Metadata JSON
- Chapter markers

All deliverables are stored in S3 and include file metadata.
"""

from pydantic import BaseModel, HttpUrl, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class DeliverableType(str, Enum):
    """Types of deliverable files generated from audiobook jobs."""

    FULL_AUDIOBOOK = "full_audiobook"
    CHAPTER_AUDIO = "chapter_audio"
    SCRIPT_TEXT = "script_text"
    METADATA_JSON = "metadata_json"
    CHAPTER_MARKERS = "chapter_markers"
    SCRIPTS_ARCHIVE = "scripts_archive"


class DeliverableResponse(BaseModel):
    """
    Schema for deliverable file metadata.
    
    Represents a single output file from the audiobook generation process,
    including S3 storage location and file metadata.
    """

    id: uuid.UUID
    job_id: uuid.UUID
    file_type: str
    s3_url: HttpUrl
    file_size_bytes: int
    mime_type: str
    filename: str
    chapter_number: Optional[int] = None
    duration_seconds: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("file_size_bytes")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Ensure file size is positive and reasonable."""
        if v < 0:
            raise ValueError("File size cannot be negative")
        if v > 5_000_000_000:  # 5GB max
            raise ValueError("File size exceeds maximum allowed (5GB)")
        return v

    @field_validator("duration_seconds")
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """Ensure duration is positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Duration cannot be negative")
        return v


class DeliverableListResponse(BaseModel):
    """Schema for list of deliverables with aggregate metadata."""

    deliverables: List[DeliverableResponse]
    total_size_bytes: int
    total_files: int
    total_duration_seconds: Optional[int] = None

    @field_validator("total_size_bytes")
    @classmethod
    def validate_total_size(cls, v: int) -> int:
        """Ensure total size is non-negative."""
        if v < 0:
            raise ValueError("Total size cannot be negative")
        return v

    @field_validator("total_files")
    @classmethod
    def validate_total_files(cls, v: int) -> int:
        """Ensure file count is non-negative."""
        if v < 0:
            raise ValueError("Total files cannot be negative")
        return v
