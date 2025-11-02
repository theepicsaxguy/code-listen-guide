"""Pydantic schemas for Episode resources."""

from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime


class EpisodeResponse(BaseModel):
    id: str
    job_id: str
    episode_number: int
    title: str
    narrative_theme: str
    file_clusters: Optional[Dict[str, List[str]]]
    dependency_graph: Optional[Dict[str, List[str]]]
    architectural_boundary: Optional[str]
    conversation_hooks: Optional[List[str]]
    learning_objectives: Optional[List[str]]
    goals: Optional[List[str] | Dict[str, Any]]
    dependency_inputs: Optional[List[str] | Dict[str, Any]]
    dependency_outputs: Optional[List[str] | Dict[str, Any]]
    depends_on: Optional[List[str]]
    leads_to: Optional[List[str]]
    estimated_duration_minutes: Optional[int]
    estimated_tokens: Optional[int]
    status: Optional[str]
    dialogue_script: Optional[str]
    audio_url: Optional[str]
    duration_seconds: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class EpisodesListResponse(BaseModel):
    episodes: List[EpisodeResponse]
    total: int
