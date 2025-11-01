"""Schemas for trace querying and replay endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobTraceStage(BaseModel):
    name: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    logs_url: Optional[str] = None


class JobTraceResponse(BaseModel):
    id: str
    job_id: str
    user_id: str
    repo_url: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    stages: List[JobTraceStage]
    tool_traces: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)


class StageReplayResponse(BaseModel):
    success: bool
    job_id: str
    stage: str
    requested_at: str
    message: str
