"""
Pydantic schemas for Outline-related requests and responses.

TODO: Implementation steps:
1. Define OutlineChapter schema for chapter structure
2. Define OutlineResponse schema
3. Define OutlineUpdate schema for user modifications
4. Add validation for outline structure
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class OutlineChapter(BaseModel):
    """Schema for a single chapter in the outline."""

    number: int = Field(ge=1)
    title: str = Field(default="")
    description: str = Field(default="")
    estimated_duration_minutes: int = Field(default=0, ge=0)
    files_covered: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _coerce_numbers(cls, values: Any) -> Any:
        if isinstance(values, dict):
            data = dict(values)
            if "number" in data:
                try:
                    data["number"] = int(data["number"])
                except (TypeError, ValueError):
                    data["number"] = 0
            if "estimated_duration_minutes" in data:
                try:
                    data["estimated_duration_minutes"] = int(
                        data["estimated_duration_minutes"]
                    )
                except (TypeError, ValueError):
                    data["estimated_duration_minutes"] = 0
            return data
        return values


class OutlineData(BaseModel):
    """Schema for complete outline structure."""

    chapters: List[OutlineChapter]
    total_estimated_duration_minutes: Optional[int] = None
    total_chapters: Optional[int] = None
    depth_tier: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def _populate_totals(self) -> "OutlineData":
        minutes = self.total_estimated_duration_minutes
        if minutes is None:
            minutes = sum(
                max(chapter.estimated_duration_minutes, 0) for chapter in self.chapters
            )
        chapter_count = self.total_chapters or len(self.chapters)
        object.__setattr__(self, "total_estimated_duration_minutes", minutes)
        object.__setattr__(self, "total_chapters", chapter_count)
        return self


class OutlineGenerateRequest(BaseModel):
    """Payload required to generate an outline for a job."""

    analysis_data: Dict[str, Any]


class OutlineResponse(BaseModel):
    """Schema for outline in responses."""

    id: uuid.UUID
    job_id: uuid.UUID
    outline_data: OutlineData
    user_approved: bool
    user_modifications: Optional[Dict[str, Any]] = None
    created_at: datetime
    approved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class OutlineUpdate(BaseModel):
    """Schema for updating outline with user modifications."""

    outline_data: OutlineData
    user_modifications: Optional[Dict[str, Any]] = None


class OutlineApprove(BaseModel):
    """Schema for approving outline (triggers payment)."""

    outline_id: uuid.UUID
    payment_amount_cents: Optional[int] = Field(default=None, ge=0)
