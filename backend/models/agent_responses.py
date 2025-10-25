"""Shared Pydantic schemas for structured agent responses."""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OutlineChapterResponse(BaseModel):
    """Single chapter entry returned by the outline agent."""

    number: int = Field(ge=1)
    title: str = Field(default="")
    description: str = Field(default="")
    estimated_duration_minutes: int = Field(default=0, ge=0)
    files_covered: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _coerce_numbers(cls, value: Any) -> Any:
        if isinstance(value, dict):
            data = dict(value)
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
        return value


class OutlineAgentResponse(BaseModel):
    """Top-level payload produced by the outline agent."""

    chapters: List[OutlineChapterResponse] = Field(default_factory=list)
    depth_tier: Optional[str] = None
    total_estimated_duration_minutes: Optional[int] = None
    total_chapters: Optional[int] = None
    raw_outline: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _from_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"chapters": [], "raw_outline": value.strip()}
        return value

    @model_validator(mode="after")
    def _populate_totals(self) -> "OutlineAgentResponse":
        minutes = self.total_estimated_duration_minutes
        if minutes is None:
            minutes = sum(
                max(chapter.estimated_duration_minutes, 0) for chapter in self.chapters
            )
        chapter_count = self.total_chapters or len(self.chapters)
        object.__setattr__(self, "total_estimated_duration_minutes", minutes)
        object.__setattr__(self, "total_chapters", chapter_count)
        return self


class ScriptAgentResponse(BaseModel):
    """Narration script produced for a single chapter."""

    chapter_number: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = None
    script: str

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _from_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"script": value.strip()}
        return value


class AudioAgentResponse(BaseModel):
    """Audio synthesis result for a chapter script."""

    chapter_number: Optional[int] = Field(default=None, ge=1)
    audio_url: str
    duration_seconds: Optional[int] = Field(default=None, ge=0)

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def _from_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"audio_url": value.strip()}
        return value
