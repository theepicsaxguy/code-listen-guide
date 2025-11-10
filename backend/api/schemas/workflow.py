"""Pydantic schemas for workflow administration APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowDefinitionCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class WorkflowDefinitionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class WorkflowDefinitionOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    current_revision_id: Optional[UUID]
    current_version: Optional[int]
    created_at: datetime
    updated_at: datetime


class WorkflowStepCreate(BaseModel):
    step_order: int
    step_name: str = Field(..., max_length=255)
    agent_id: Optional[UUID] = None
    execution_mode: str
    input_mapping: Optional[Dict[str, Any]] = None
    output_mapping: Optional[Dict[str, Any]] = None
    checkpoint_enabled: bool = True
    retry_policy: Optional[Dict[str, Any]] = None
    step_config: Optional[Dict[str, Any]] = None


class WorkflowRevisionCreate(BaseModel):
    revision_metadata: Optional[Dict[str, Any]] = None
    steps: List[WorkflowStepCreate]
    publish: bool = False


class WorkflowStepOut(BaseModel):
    id: UUID
    step_order: int
    step_name: str
    execution_mode: str
    agent_id: Optional[UUID]
    checkpoint_enabled: bool
    input_mapping: Optional[Dict[str, Any]]
    output_mapping: Optional[Dict[str, Any]]
    retry_policy: Optional[Dict[str, Any]]
    step_config: Optional[Dict[str, Any]]


class WorkflowRevisionOut(BaseModel):
    id: UUID
    version: int
    is_published: bool
    revision_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    published_at: Optional[datetime]
    steps: List[WorkflowStepOut]


class RevisionValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
