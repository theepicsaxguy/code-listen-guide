"""
Pydantic schemas for Job-related requests and responses.

Provides schemas for:
- Job creation with repository validation
- Job status tracking and progress updates
- Cost estimation based on depth tier
- Paginated job listings
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
import re
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from decimal import Decimal
import uuid

from backend.utils.validators import validate_github_url

if TYPE_CHECKING:
    from backend.api.schemas.chapter import ChapterResponse
    from backend.api.schemas.deliverable import DeliverableResponse


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


def calculate_price_for_tier(depth_tier: DepthTier) -> int:
    """
    Calculate price in cents based on depth tier.
    
    Args:
        depth_tier: The selected audiobook depth tier
        
    Returns:
        Price in cents
    """
    pricing = {
        DepthTier.SURVEY: 1900,  # $19
        DepthTier.STANDARD: 4900,  # $49
        DepthTier.COMPREHENSIVE: 9900,  # $99
    }
    return pricing.get(depth_tier, 0)


class JobCreate(BaseModel):
    """
    Schema for creating a new job.
    
    Validates GitHub URL format and extracts owner/repo information.
    Ensures git ref contains only valid characters.
    """

    repo_url: str = Field(..., description="GitHub repository URL")
    depth_tier: DepthTier
    git_ref: Optional[str] = Field(default="main", description="Git branch or tag")

    @field_validator("repo_url")
    @classmethod
    def validate_github_url_format(cls, v: str) -> str:
        """Validate that repo_url is a valid GitHub URL."""
        is_valid, owner, repo = validate_github_url(v)
        if not is_valid:
            raise ValueError(
                "Invalid GitHub URL format. Expected: https://github.com/owner/repo or git@github.com:owner/repo.git"
            )
        return v

    @field_validator("git_ref")
    @classmethod
    def validate_git_ref_format(cls, v: str) -> str:
        """Validate git ref format and characters."""
        if not v:
            raise ValueError("Git ref cannot be empty")
        if len(v) > 255:
            raise ValueError("Git ref cannot exceed 255 characters")
        # Allow alphanumeric, slash, underscore, hyphen, and period
        if not re.match(r"^[a-zA-Z0-9/_.-]+$", v):
            raise ValueError(
                "Git ref contains invalid characters. Only alphanumeric, /, _, -, and . are allowed"
            )
        return v


class JobResponse(BaseModel):
    """
    Schema for job data in responses.
    
    Includes nested chapter and deliverable data for complete job representation.
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

    # Nested related data
    chapters: List["ChapterResponse"] = []
    deliverables: List["DeliverableResponse"] = []

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

    @classmethod
    def from_tier(
        cls,
        depth_tier: DepthTier,
        repo_analysis: Optional[dict] = None,
    ) -> "JobEstimate":
        """
        Create estimate from depth tier.
        
        Args:
            depth_tier: The requested audiobook depth tier
            repo_analysis: Optional repository analysis data for more accurate estimates
            
        Returns:
            JobEstimate with calculated values
        """
        estimated_cost = calculate_price_for_tier(depth_tier)
        
        # Base estimates by tier
        tier_estimates = {
            DepthTier.SURVEY: {"duration": 180, "chapters": 5},  # 2-4 hours, ~3hr avg
            DepthTier.STANDARD: {"duration": 480, "chapters": 10},  # 6-10 hours, ~8hr avg
            DepthTier.COMPREHENSIVE: {"duration": 1200, "chapters": 20},  # 15-25 hours, ~20hr avg
        }
        
        estimates = tier_estimates.get(
            depth_tier,
            {"duration": 120, "chapters": 8}
        )

        # Future enhancement: Adjust based on repo_analysis (file count, complexity, language mix)
        # if repo_analysis:
        #     file_count = repo_analysis.get("file_count", 0)
        #     # Adjust estimates based on actual repository size

        return cls(
            estimated_cost_cents=estimated_cost,
            estimated_duration_minutes=estimates["duration"],
            estimated_chapters=estimates["chapters"],
            depth_tier=depth_tier.value,
        )
    
    @field_validator("estimated_cost_cents")
    @classmethod
    def validate_cost(cls, v: int) -> int:
        """Ensure cost is non-negative and reasonable."""
        if v < 0:
            raise ValueError("Cost cannot be negative")
        if v > 1000000:  # $10,000 max
            raise ValueError("Cost exceeds maximum allowed")
        return v


# Rebuild models after all are defined to resolve forward references
from backend.api.schemas.chapter import ChapterResponse  # noqa: E402
from backend.api.schemas.deliverable import DeliverableResponse  # noqa: E402

JobResponse.model_rebuild()
