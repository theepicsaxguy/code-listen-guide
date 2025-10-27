"""
Pydantic schemas for Job-related requests and responses.

TODO: Implementation steps:
1. Define JobCreate schema
2. Define JobResponse schema with nested chapters
3. Define JobList schema for pagination
4. Add depth tier enum and validation
5. Add repository URL validation
6. Create status enums
7. Add progress tracking fields
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal
import uuid


class DepthTier(str, Enum):
    """Audiobook depth tiers."""

    SURVEY = "survey"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class JobStatus(str, Enum):
    """Job processing statuses."""

    PENDING = "pending"
    ANALYZING = "analyzing"
    SCRIPTING = "scripting"
    SYNTHESIZING = "synthesizing"
    POST_PROCESSING = "post_processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobCreate(BaseModel):
    """
    Schema for creating a new job.

    TODO:
    - Validate GitHub URL format
    - Add git ref validation
    - Estimate cost based on depth tier
    """

    repo_url: str = Field(..., description="GitHub repository URL")
    depth_tier: DepthTier
    git_ref: Optional[str] = Field(default="main", description="Git branch or tag")

    # TODO: Add validators
    # @validator("repo_url")
    # def validate_github_url(cls, v):
    #     # Ensure it's a valid GitHub URL
    #     # Extract owner and repo name
    #     pass


class JobResponse(BaseModel):
    """
    Schema for job data in responses.

    TODO:
    - Add nested chapter data
    - Add deliverables list
    - Add cost information
    """

    id: uuid.UUID
    user_id: uuid.UUID
    repo_url: str
    repo_name: str
    repo_owner: str
    git_ref: str
    depth_tier: str
    status: str
    current_stage: Optional[str]
    progress_percentage: Decimal
    error_message: Optional[str]
    estimated_duration_minutes: Optional[int]
    estimated_chapters: Optional[int]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    # TODO: Add nested schemas
    # chapters: List["ChapterResponse"] = []
    # deliverables: List["DeliverableResponse"] = []

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for paginated job list."""

    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class JobEstimateRequest(BaseModel):
    """Schema for requesting a job cost estimate."""

    repo_url: HttpUrl = Field(..., description="Git repository URL to analyze")
    depth_tier: DepthTier = Field(..., description="Requested audiobook depth tier")


class JobEstimate(BaseModel):
    """Schema for job cost and time estimate."""

    estimated_cost_cents: int = Field(..., ge=0)
    estimated_duration_minutes: int = Field(..., ge=0)
    estimated_chapters: int = Field(..., ge=0)
    depth_tier: str
