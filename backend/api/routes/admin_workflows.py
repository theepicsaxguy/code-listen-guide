"""Admin API for managing workflow definitions and revisions."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from backend.api.dependencies import require_admin
from backend.api.schemas.workflow import (
    RevisionValidationResult,
    WorkflowDefinitionCreate,
    WorkflowDefinitionUpdate,
    WorkflowDefinitionOut,
    WorkflowRevisionCreate,
    WorkflowRevisionOut,
    WorkflowStepOut,
)
from backend.db.session import get_db
from backend.models.agent_registry import AgentRegistry
from backend.models.workflow_definition import WorkflowDefinition
from backend.models.workflow_revision import WorkflowRevision
from backend.models.workflow_step import WorkflowStep
from backend.workflows.dynamic_loader import get_workflow_manager


router = APIRouter(prefix="/api/v1/admin/workflows", tags=["admin", "workflows"])


def _definition_to_out(definition: WorkflowDefinition) -> WorkflowDefinitionOut:
    current_revision = definition.current_revision
    return WorkflowDefinitionOut(
        id=definition.id,
        name=definition.name,
        description=definition.description,
        current_revision_id=current_revision.id if current_revision else None,
        current_version=current_revision.version if current_revision else None,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
    )


def _revision_to_out(revision: WorkflowRevision) -> WorkflowRevisionOut:
    steps = [
        WorkflowStepOut(
            id=step.id,
            step_order=step.step_order,
            step_name=step.step_name,
            execution_mode=step.execution_mode,
            agent_id=step.agent_id,
            plugin_id=step.plugin_id,
            checkpoint_enabled=bool(step.checkpoint_enabled),
            input_mapping=step.input_mapping,
            output_mapping=step.output_mapping,
            retry_policy=step.retry_policy,
            step_config=step.step_config,
        )
        for step in sorted(revision.steps, key=lambda item: item.step_order)
    ]
    return WorkflowRevisionOut(
        id=revision.id,
        version=revision.version,
        is_published=bool(revision.is_published),
        revision_metadata=revision.revision_metadata,
        created_at=revision.created_at,
        published_at=revision.published_at,
        steps=steps,
    )


def _validate_revision(revision: WorkflowRevision) -> RevisionValidationResult:
    errors: List[str] = []
    ordered = sorted(revision.steps, key=lambda step: step.step_order)
    if not ordered:
        errors.append("Revision must define at least one step")
        return RevisionValidationResult(is_valid=False, errors=errors)

    step_orders = [step.step_order for step in ordered]
    if len(step_orders) != len(set(step_orders)):
        errors.append("Duplicate step_order values detected")

    expected_order = list(range(len(ordered)))
    if step_orders != expected_order:
        errors.append("step_order values must be contiguous starting at 0")

    for step in ordered:
        if step.execution_mode not in {"sequential", "concurrent", "conditional"}:
            errors.append(f"Unsupported execution_mode '{step.execution_mode}'")
        # A step must have either an agent_id OR plugin_id (or both), unless it's conditional
        if step.agent_id is None and step.plugin_id is None and step.execution_mode != "conditional":
            errors.append(f"Step '{step.step_name}' requires either an agent or a plugin")

    return RevisionValidationResult(is_valid=not errors, errors=errors)


@router.get("", operation_id="listWorkflows", response_model=List[WorkflowDefinitionOut])
async def list_workflows(
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    definitions = (
        db.query(WorkflowDefinition)
        .options(selectinload(WorkflowDefinition.current_revision))
        .order_by(WorkflowDefinition.created_at.asc())
        .all()
    )
    return [_definition_to_out(defn) for defn in definitions]


@router.post("", operation_id="createWorkflow", response_model=WorkflowDefinitionOut, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowDefinitionCreate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    existing = (
        db.query(WorkflowDefinition)
        .filter(func.lower(WorkflowDefinition.name) == payload.name.lower())
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Workflow with that name already exists")

    definition = WorkflowDefinition(name=payload.name, description=payload.description)
    db.add(definition)
    db.commit()
    db.refresh(definition)
    return _definition_to_out(definition)


@router.patch("/{workflow_id}", operation_id="updateWorkflowDefinition", response_model=WorkflowDefinitionOut)
async def update_workflow_definition(
    workflow_id: UUID,
    payload: WorkflowDefinitionUpdate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """
    Update workflow definition metadata (name, description).

    This endpoint updates the workflow definition itself, not its revisions or steps.
    To modify steps, create a new revision instead.
    """
    definition = db.get(WorkflowDefinition, workflow_id)
    if definition is None:
        raise HTTPException(status_code=404, detail="Workflow definition not found")

    # Check for name conflicts if name is being updated
    if payload.name is not None and payload.name != definition.name:
        existing = (
            db.query(WorkflowDefinition)
            .filter(
                func.lower(WorkflowDefinition.name) == payload.name.lower(),
                WorkflowDefinition.id != workflow_id
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="Workflow with that name already exists")
        definition.name = payload.name

    if payload.description is not None:
        definition.description = payload.description

    db.commit()
    db.refresh(definition)

    # Reload with current_revision relationship
    definition = (
        db.query(WorkflowDefinition)
        .options(selectinload(WorkflowDefinition.current_revision))
        .filter(WorkflowDefinition.id == workflow_id)
        .one()
    )

    return _definition_to_out(definition)


@router.get("/{workflow_id}/revisions", operation_id="listWorkflowRevisions", response_model=List[WorkflowRevisionOut])
async def list_workflow_revisions(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    revisions = (
        db.query(WorkflowRevision)
        .options(selectinload(WorkflowRevision.steps))
        .filter(WorkflowRevision.workflow_definition_id == workflow_id)
        .order_by(WorkflowRevision.version.asc())
        .all()
    )
    return [_revision_to_out(revision) for revision in revisions]


@router.post(
    "/{workflow_id}/revisions",
    operation_id="createWorkflowRevision",
    response_model=WorkflowRevisionOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_revision(
    workflow_id: UUID,
    payload: WorkflowRevisionCreate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    definition = db.get(WorkflowDefinition, workflow_id)
    if definition is None:
        raise HTTPException(status_code=404, detail="Workflow definition not found")

    if not payload.steps:
        raise HTTPException(status_code=400, detail="Revisions require at least one step")

    # Validate that agents and plugins exist
    for step in payload.steps:
        if step.agent_id is not None:
            if db.get(AgentRegistry, step.agent_id) is None:
                raise HTTPException(status_code=400, detail=f"Agent {step.agent_id} not found")
        if step.plugin_id is not None:
            from backend.models.tool_registry import ToolRegistry
            if db.get(ToolRegistry, step.plugin_id) is None:
                raise HTTPException(status_code=400, detail=f"Plugin {step.plugin_id} not found")

    latest_version: Optional[int] = (
        db.query(func.max(WorkflowRevision.version))
        .filter(WorkflowRevision.workflow_definition_id == workflow_id)
        .scalar()
    )
    next_version = (latest_version or 0) + 1

    revision = WorkflowRevision(
        workflow_definition_id=workflow_id,
        version=next_version,
        is_published=False,
        revision_metadata=payload.revision_metadata,
    )
    db.add(revision)
    db.flush()

    for step_payload in payload.steps:
        step = WorkflowStep(
            revision_id=revision.id,
            step_order=step_payload.step_order,
            step_name=step_payload.step_name,
            agent_id=step_payload.agent_id,
            plugin_id=step_payload.plugin_id,
            execution_mode=step_payload.execution_mode,
            input_mapping=step_payload.input_mapping,
            output_mapping=step_payload.output_mapping,
            checkpoint_enabled=step_payload.checkpoint_enabled,
            retry_policy=step_payload.retry_policy,
            step_config=step_payload.step_config,
        )
        db.add(step)

    if payload.publish:
        revision.is_published = True
        revision.published_at = datetime.utcnow()
        definition.current_revision_id = revision.id

    db.commit()
    db.refresh(revision)

    manager = get_workflow_manager()
    manager.refresh_revision(revision.id)
    return _revision_to_out(revision)


@router.get(
    "/{workflow_id}/revisions/{revision_id}",
    operation_id="getWorkflowRevision",
    response_model=WorkflowRevisionOut,
)
async def get_revision(
    workflow_id: UUID,
    revision_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    revision = (
        db.query(WorkflowRevision)
        .options(selectinload(WorkflowRevision.steps))
        .filter(
            WorkflowRevision.id == revision_id,
            WorkflowRevision.workflow_definition_id == workflow_id,
        )
        .one_or_none()
    )
    if revision is None:
        raise HTTPException(status_code=404, detail="Workflow revision not found")
    return _revision_to_out(revision)


@router.post(
    "/{workflow_id}/revisions/{revision_id}/publish",
    operation_id="publishWorkflowRevision",
    response_model=WorkflowRevisionOut,
)
async def publish_revision(
    workflow_id: UUID,
    revision_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    revision = (
        db.query(WorkflowRevision)
        .options(selectinload(WorkflowRevision.steps))
        .filter(
            WorkflowRevision.id == revision_id,
            WorkflowRevision.workflow_definition_id == workflow_id,
        )
        .one_or_none()
    )
    if revision is None:
        raise HTTPException(status_code=404, detail="Workflow revision not found")

    definition = db.get(WorkflowDefinition, workflow_id)
    if definition is None:
        raise HTTPException(status_code=404, detail="Workflow definition not found")

    validation = _validate_revision(revision)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.errors)

    revision.is_published = True
    revision.published_at = datetime.utcnow()
    definition.current_revision_id = revision.id
    db.commit()
    db.refresh(revision)

    manager = get_workflow_manager()
    manager.refresh_revision(revision.id)
    return _revision_to_out(revision)


@router.post(
    "/{workflow_id}/revisions/{revision_id}/validate",
    operation_id="validateWorkflowRevision",
    response_model=RevisionValidationResult,
)
async def validate_revision_endpoint(
    workflow_id: UUID,
    revision_id: UUID,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    revision = (
        db.query(WorkflowRevision)
        .options(selectinload(WorkflowRevision.steps))
        .filter(
            WorkflowRevision.id == revision_id,
            WorkflowRevision.workflow_definition_id == workflow_id,
        )
        .one_or_none()
    )
    if revision is None:
        raise HTTPException(status_code=404, detail="Workflow revision not found")
    return _validate_revision(revision)
