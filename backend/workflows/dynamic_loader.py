"""Dynamic workflow loading utilities for database-backed workflows."""

from __future__ import annotations

import contextlib
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from backend.db.session import SessionLocal
from backend.models.workflow_definition import WorkflowDefinition
from backend.models.workflow_instance import WorkflowInstance
from backend.models.workflow_revision import WorkflowRevision
from backend.models.workflow_step import WorkflowStep


@dataclass(frozen=True)
class AgentDescriptor:
    """Description of an agent factory registered for workflow execution."""

    id: UUID
    name: str
    module_path: str
    factory_function: str


@dataclass(frozen=True)
class StepDescriptor:
    """Description of a workflow step belonging to a revision."""

    id: UUID
    order: int
    name: str
    execution_mode: str
    checkpoint_enabled: bool
    input_mapping: Dict[str, Any]
    output_mapping: Dict[str, Any]
    retry_policy: Optional[Dict[str, Any]]
    step_config: Dict[str, Any]
    agent: Optional[AgentDescriptor]


@dataclass(frozen=True)
class RevisionDescriptor:
    """Immutable representation of a workflow revision with ordered steps."""

    id: UUID
    workflow_id: UUID
    workflow_name: str
    version: int
    is_published: bool
    metadata: Dict[str, Any]
    steps: List[StepDescriptor]


class WorkflowManager:
    """Load workflow revisions and manage workflow instance state."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._revision_cache: Dict[UUID, RevisionDescriptor] = {}

    @contextlib.contextmanager
    def _session_scope(self) -> Iterator[Session]:
        session: Session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def _build_agent_descriptor(self, step: WorkflowStep) -> Optional[AgentDescriptor]:
        agent = step.agent
        if agent is None:
            return None
        return AgentDescriptor(
            id=agent.id,
            name=agent.name,
            module_path=agent.module_path,
            factory_function=agent.factory_function,
        )

    def _build_step_descriptor(self, step: WorkflowStep) -> StepDescriptor:
        return StepDescriptor(
            id=step.id,
            order=step.step_order,
            name=step.step_name,
            execution_mode=step.execution_mode,
            checkpoint_enabled=bool(step.checkpoint_enabled),
            input_mapping=step.input_mapping or {},
            output_mapping=step.output_mapping or {},
            retry_policy=step.retry_policy or None,
            step_config=step.step_config or {},
            agent=self._build_agent_descriptor(step),
        )

    def _build_revision_descriptor(self, revision: WorkflowRevision) -> RevisionDescriptor:
        steps = sorted((self._build_step_descriptor(step) for step in revision.steps), key=lambda s: s.order)
        metadata = revision.revision_metadata or {}
        return RevisionDescriptor(
            id=revision.id,
            workflow_id=revision.workflow_definition_id,
            workflow_name=revision.workflow_definition.name,
            version=revision.version,
            is_published=bool(revision.is_published),
            metadata=metadata,
            steps=steps,
        )

    def _load_revision_from_db(self, revision_id: UUID) -> RevisionDescriptor:
        with self._session_scope() as session:
            revision: Optional[WorkflowRevision] = (
                session.query(WorkflowRevision)
                .options(
                    selectinload(WorkflowRevision.workflow_definition),
                    selectinload(WorkflowRevision.steps).selectinload(WorkflowStep.agent),
                )
                .filter(WorkflowRevision.id == revision_id)
                .one_or_none()
            )
            if revision is None:
                raise ValueError(f"Workflow revision {revision_id} not found")
            return self._build_revision_descriptor(revision)

    def load_revision(self, revision_id: UUID) -> RevisionDescriptor:
        """Return a cached revision descriptor, loading from the database if necessary."""

        with self._lock:
            descriptor = self._revision_cache.get(revision_id)
            if descriptor is None:
                descriptor = self._load_revision_from_db(revision_id)
                self._revision_cache[revision_id] = descriptor
            return descriptor

    def get_current_revision(self, workflow_name: str) -> RevisionDescriptor:
        """Return the published revision for the given workflow name."""

        with self._session_scope() as session:
            definition: Optional[WorkflowDefinition] = (
                session.query(WorkflowDefinition)
                .options(selectinload(WorkflowDefinition.current_revision))
                .filter(WorkflowDefinition.name == workflow_name)
                .one_or_none()
            )
            if definition is None or definition.current_revision is None:
                raise ValueError(f"Workflow '{workflow_name}' has no published revision")
            return self.load_revision(definition.current_revision.id)

    def refresh_revision(self, revision_id: UUID) -> None:
        """Force-refresh the cached descriptor for a revision."""

        with self._lock:
            self._revision_cache.pop(revision_id, None)
            descriptor = self._load_revision_from_db(revision_id)
            self._revision_cache[revision_id] = descriptor

    def reload_registry(self) -> None:
        """Clear cached revisions so future calls load fresh data."""

        with self._lock:
            self._revision_cache.clear()

    def _coerce_uuid(self, value: Any) -> UUID:
        if isinstance(value, UUID):
            return value
        return UUID(str(value))

    def _default_instance_state(self, *, revision: RevisionDescriptor, job_context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "revision_id": str(revision.id),
            "job": job_context,
            "steps": {},
        }

    def ensure_instance(
        self,
        *,
        job_id: Any,
        revision: RevisionDescriptor,
        job_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Ensure a workflow instance record exists and return its state payload."""

        normalized_job_id = self._coerce_uuid(job_id)
        now = datetime.utcnow()
        with self._session_scope() as session:
            instance: Optional[WorkflowInstance] = (
                session.query(WorkflowInstance)
                .filter(WorkflowInstance.id == normalized_job_id)
                .one_or_none()
            )
            if instance is None:
                state = self._default_instance_state(revision=revision, job_context=job_context)
                instance = WorkflowInstance(
                    id=normalized_job_id,
                    job_id=normalized_job_id,
                    revision_id=revision.id,
                    status="running",
                    started_at=now,
                    instance_state=state,
                )
                session.add(instance)
                session.commit()
                return state

            state_payload = instance.instance_state or {}
            if not state_payload:
                state_payload = self._default_instance_state(revision=revision, job_context=job_context)
                instance.instance_state = state_payload
            if instance.started_at is None:
                instance.started_at = now
            if instance.revision_id != revision.id:
                instance.revision_id = revision.id
            if instance.status == "pending":
                instance.status = "running"
            session.commit()
            return state_payload

    def update_instance(
        self,
        *,
        job_id: Any,
        current_step_id: Optional[UUID] = None,
        status: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        completed: bool = False,
    ) -> None:
        """Persist workflow instance progress."""

        normalized_job_id = self._coerce_uuid(job_id)
        with self._session_scope() as session:
            instance: Optional[WorkflowInstance] = (
                session.query(WorkflowInstance)
                .filter(WorkflowInstance.id == normalized_job_id)
                .one_or_none()
            )
            if instance is None:
                raise ValueError(f"Workflow instance {normalized_job_id} not found")
            if current_step_id is not None:
                instance.current_step_id = current_step_id
            if status is not None:
                instance.status = status
            if state is not None:
                instance.instance_state = state
            if completed:
                instance.completed_at = datetime.utcnow()
                if status is None:
                    instance.status = "completed"
            session.commit()

    def get_instance_state(self, job_id: Any) -> Dict[str, Any]:
        """Return the stored instance state for the provided job."""

        normalized_job_id = self._coerce_uuid(job_id)
        with self._session_scope() as session:
            instance: Optional[WorkflowInstance] = (
                session.query(WorkflowInstance)
                .filter(WorkflowInstance.id == normalized_job_id)
                .one_or_none()
            )
            if instance is None:
                raise ValueError(f"Workflow instance {normalized_job_id} not found")
            payload = instance.instance_state or {}
            return payload


_MANAGER = WorkflowManager()


def get_workflow_manager() -> WorkflowManager:
    """Return the shared workflow manager singleton."""

    return _MANAGER
