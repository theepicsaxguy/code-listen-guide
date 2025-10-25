"""
Pydantic schemas for Chapter-related responses.

TODO: Implementation steps:
1. Define ChapterResponse schema
2. Add audio metadata fields
3. Create chapter list response
4. Add status tracking
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class ChapterResponse(BaseModel):
    """
    Schema for chapter data in responses.

    TODO:
    - Add all fields from Chapter model
    - Include audio playback metadata
    """

    id: uuid.UUID
    job_id: uuid.UUID
    chapter_number: int
    title: str
    description: Optional[str]
    files_covered: List[str]
    topics_covered: List[str]
    status: str
    audio_url: Optional[str]
    audio_duration_seconds: Optional[int]
    start_timestamp_ms: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChapterListResponse(BaseModel):
    """Schema for list of chapters."""

    chapters: List[ChapterResponse]
    total_chapters: int
    total_duration_seconds: int
