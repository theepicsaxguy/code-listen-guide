"""Trace API exposing workflow execution metadata and replay controls."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from backend.api.dependencies import get_current_user, require_admin
from backend.api.schemas.trace import JobTraceResponse, JobTraceStage, StageReplayResponse
from backend.db.session import get_db
from backend.models.job import Job
from backend.models.user import User
from backend.models.workflow_instance import WorkflowInstance
from backend.models.workflow_revision import WorkflowRevision


router = APIRouter(prefix="/api/v1/traces", tags=["traces"])

DEFAULT_STAGE_SEQUENCE: Sequence[str] = (
    "analysis",
    "outline",
    "approval",
    "scripting",
    "audio",
    "post_processing",
)


def _normalize_stage_name(stage: Optional[str]) -> Optional[str]:
    if not stage:
        return None
    normalized = stage.strip().lower()
    if normalized == "postprocess":
        return "post_processing"
    return normalized


def _ordered_stage_names(instance: Optional[WorkflowInstance]) -> List[str]:
    if instance and instance.revision and instance.revision.steps:
        sorted_steps = sorted(instance.revision.steps, key=lambda step: step.step_order)
        return [step.step_name for step in sorted_steps]
    return list(DEFAULT_STAGE_SEQUENCE)


def _extract_tool_traces(steps_state: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    traces: Dict[str, List[Dict[str, Any]]] = {}
    for step_name, payload in steps_state.items():
        tool_calls = payload.get("tool_calls") if isinstance(payload, dict) else None
        if isinstance(tool_calls, list):
            sanitized: List[Dict[str, Any]] = []
            for call in tool_calls:
                if isinstance(call, dict):
                    sanitized.append(dict(call))
            if sanitized:
                traces[step_name] = sanitized
    return traces


def _last_error(tool_calls: Iterable[Dict[str, Any]], fallback: Optional[str]) -> Optional[str]:
    for call in reversed(list(tool_calls)):
        error_value = call.get("error")
        if error_value:
            return str(error_value)
    return fallback


def _aggregate_duration(tool_calls: Iterable[Dict[str, Any]]) -> Optional[float]:
    durations: List[float] = []
    for call in tool_calls:
        value = call.get("duration_ms")
        if isinstance(value, (int, float)):
            durations.append(float(value))
    if not durations:
        return None
    return float(sum(durations))


def _derive_stage_status(
    *,
    step_name: str,
    job: Job,
    ordered_names: Sequence[str],
    steps_state: Dict[str, Any],
    tool_calls: List[Dict[str, Any]],
) -> str:
    normalized_stage = _normalize_stage_name(job.current_stage)
    current_index = None
    if normalized_stage and normalized_stage in ordered_names:
        current_index = ordered_names.index(normalized_stage)
    step_index = ordered_names.index(step_name) if step_name in ordered_names else None
    has_state = step_name in steps_state
    if job.status == "failed":
        if tool_calls:
            status_flag = next(
                (call.get("status") for call in reversed(tool_calls) if isinstance(call.get("status"), str)),
                None,
            )
            if status_flag in {"error", "forbidden"}:
                return "failed"
        if step_index is not None and step_index == current_index:
            return "failed"
        if has_state:
            return "completed"
        return "pending"
    if job.status == "completed":
        return "completed"
    if has_state and job.status != "running":
        return "completed"
    if step_index is not None and step_index == current_index:
        if job.status in {"running", "waiting_approval"}:
            return "running"
        if has_state:
            return "completed"
        return "pending"
    if current_index is not None and step_index is not None and step_index < current_index:
        return "completed"
    return "pending"


@router.get("/{job_id}", response_model=JobTraceResponse)
async def get_job_trace(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobTraceResponse:
    job = db.query(Job).filter(Job.id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.user_id != current_user.id and not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access trace")
    instance = (
        db.query(WorkflowInstance)
        .options(
            joinedload(WorkflowInstance.revision).joinedload(WorkflowRevision.steps)
        )
        .filter(WorkflowInstance.id == job.id)
        .one_or_none()
    )
    state_payload: Dict[str, Any] = {}
    if instance and isinstance(instance.instance_state, dict):
        state_payload = instance.instance_state
    steps_state = state_payload.get("steps") if isinstance(state_payload.get("steps"), dict) else {}
    ordered_names = _ordered_stage_names(instance)
    stages: List[JobTraceStage] = []
    tool_traces = _extract_tool_traces(steps_state)
    for name in ordered_names:
        step_payload = steps_state.get(name, {}) if isinstance(steps_state, dict) else {}
        tool_calls = tool_traces.get(name, [])
        started_at = None
        if tool_calls:
            first_call = tool_calls[0]
            started_at = first_call.get("called_at") if isinstance(first_call.get("called_at"), str) else None
        completed_at = None
        if isinstance(step_payload, dict):
            timestamp = step_payload.get("updated_at")
            if isinstance(timestamp, str):
                completed_at = timestamp
        error_detail = _last_error(tool_calls, job.error_message if _normalize_stage_name(job.current_stage) == name and job.status == "failed" else None)
        stage_status = _derive_stage_status(
            step_name=name,
            job=job,
            ordered_names=ordered_names,
            steps_state=steps_state if isinstance(steps_state, dict) else {},
            tool_calls=tool_calls,
        )
        stages.append(
            JobTraceStage(
                name=name,
                status=stage_status,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=_aggregate_duration(tool_calls),
                error=error_detail,
            )
        )
    return JobTraceResponse(
        id=str(job.id),
        job_id=str(job.id),
        user_id=str(job.user_id) if job.user_id else "",
        repo_url=job.repo_url,
        status=job.status,
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error=job.error_message,
        stages=stages,
        tool_traces=tool_traces,
    )


@router.post("/{job_id}/stages/{stage_name}/replay", response_model=StageReplayResponse, status_code=status.HTTP_202_ACCEPTED)
async def replay_stage(
    job_id: UUID,
    stage_name: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
) -> StageReplayResponse:
    job = db.query(Job).filter(Job.id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    instance = (
        db.query(WorkflowInstance)
        .options(
            joinedload(WorkflowInstance.revision).joinedload(WorkflowRevision.steps)
        )
        .filter(WorkflowInstance.id == job.id)
        .one_or_none()
    )
    normalized_stage = _normalize_stage_name(stage_name)
    if not normalized_stage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage name")
    ordered_names = _ordered_stage_names(instance)
    if normalized_stage not in ordered_names:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")
    metadata: Dict[str, Any] = dict(job.metadata_json or {})
    replay_history = list(metadata.get("replay_requests", []))
    requested_at = datetime.utcnow().isoformat()
    replay_history.append(
        {
            "stage": normalized_stage,
            "requested_by": str(current_admin.id),
            "requested_at": requested_at,
        }
    )
    metadata["replay_requests"] = replay_history
    job.metadata_json = metadata
    db.commit()
    return StageReplayResponse(
        success=True,
        job_id=str(job.id),
        stage=normalized_stage,
        requested_at=requested_at,
        message="Replay scheduled",
    )


__all__ = ["router"]
