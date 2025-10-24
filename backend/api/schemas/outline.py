"""
Pydantic schemas for Outline-related requests and responses.

TODO: Implementation steps:
1. Define OutlineChapter schema for chapter structure
2. Define OutlineResponse schema
3. Define OutlineUpdate schema for user modifications
4. Add validation for outline structure
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class OutlineChapter(BaseModel):
    """
    Schema for a single chapter in the outline.

    TODO:
    - Match structure from outline generation
    - Add all fields needed for chapter planning
    """
    number: int
    title: str
    description: str
    estimated_duration_minutes: int
    files_covered: List[str]
    topics: List[str]
    learning_objectives: List[str]


class OutlineData(BaseModel):
    """Schema for complete outline structure."""
    chapters: List[OutlineChapter]
    total_estimated_duration_minutes: int
    total_chapters: int


class OutlineResponse(BaseModel):
    """
    Schema for outline in responses.

    TODO:
    - Include approval status
    - Add modification tracking
    """
    id: uuid.UUID
    job_id: uuid.UUID
    outline_data: OutlineData
    user_approved: bool
    created_at: datetime
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


class OutlineUpdate(BaseModel):
    """Schema for updating outline with user modifications."""
    chapters: List[OutlineChapter]
    modifications: Optional[Dict[str, Any]] = None


class OutlineApprove(BaseModel):
    """Schema for approving outline (triggers payment)."""
    outline_id: uuid.UUID
