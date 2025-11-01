"""Dynamic workflow loading utilities for database-backed workflows."""

from __future__ import annotations

import contextlib
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from backend.db.session import SessionLocal
from backend.models.agent_registry import AgentRegistry
from backend.models.tool_registry import ToolRegistry
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
    description: Optional[str]
    config_schema: Dict[str, Any]
    allowed_tools: Tuple[str, ...]
    model_identifier: Optional[str]
    provider: Optional[str]
    system_prompt: Optional[str]
    memory_pointers: Tuple[str, ...]
    rollout_enabled: bool
    rollout_stage: Optional[str]
    access_policies: Dict[str, Any]
    quota_limits: Dict[str, Any]
    approval_requirements: Dict[str, Any]


@dataclass(frozen=True)
class ToolDescriptor:
    """Description of a plugin/tool exposed to the orchestration runtime."""

    id: UUID
    name: str
    stable_slug: str
    semantic_version: str
    module_path: str
    function_name: str
    description: Optional[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    owning_team: str
    authorization_scope: str
    approval_mode: str
    cost_profile: Dict[str, Any]


class ToolRegistryManager:
    """Load and cache plugin metadata for runtime execution."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_id: Dict[UUID, ToolDescriptor] = {}
        self._by_name: Dict[str, ToolDescriptor] = {}
        self._by_slug: Dict[str, ToolDescriptor] = {}
        self._by_slug_version: Dict[Tuple[str, str], ToolDescriptor] = {}

    @contextlib.contextmanager
    def _session_scope(self) -> Iterator[Session]:
        session: Session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @staticmethod
    def _version_key(value: str) -> Tuple[int, ...]:
        parts: List[int] = []
        for segment in value.split('.'):
            numeric = ''.join(character for character in segment if character.isdigit())
            parts.append(int(numeric) if numeric else 0)
        return tuple(parts)

    @staticmethod
    def _parse_slug_reference(reference: str) -> Optional[Tuple[str, str]]:
        if '@' not in reference:
            return None
        slug, version = reference.split('@', 1)
        slug_value = slug.strip().lower()
        version_value = version.strip()
        if not slug_value or not version_value:
            return None
        return slug_value, version_value

    def _lookup_cached(self, reference: Any) -> Optional[ToolDescriptor]:
        if isinstance(reference, UUID):
            return self._by_id.get(reference)
        candidate: Optional[ToolDescriptor] = None
        if reference is None:
            return None
        text = str(reference)
        try:
            ref_uuid = UUID(text)
        except (TypeError, ValueError):
            pass
        else:
            candidate = self._by_id.get(ref_uuid)
            if candidate is not None:
                return candidate
        lowered = text.lower()
        candidate = self._by_name.get(text) or self._by_name.get(lowered)
        if candidate is not None:
            return candidate
        slug_candidate = self._by_slug.get(lowered)
        if slug_candidate is not None:
            return slug_candidate
        slug_reference = self._parse_slug_reference(text)
        if slug_reference is not None:
            cached = self._by_slug_version.get(slug_reference)
            if cached is not None:
                return cached
        return None

    def _store_descriptor(self, descriptor: ToolDescriptor) -> None:
        self._by_id[descriptor.id] = descriptor
        name_candidates: set[str] = set()
        for candidate in (
            descriptor.name,
            descriptor.function_name,
            descriptor.module_path,
            f"{descriptor.module_path}.{descriptor.function_name}",
        ):
            if not candidate:
                continue
            name_candidates.add(candidate)
            name_candidates.add(candidate.lower())
        for key in name_candidates:
            self._by_name[key] = descriptor
        slug_key = descriptor.stable_slug.lower()
        existing = self._by_slug.get(slug_key)
        if existing is None or self._version_key(descriptor.semantic_version) >= self._version_key(existing.semantic_version):
            self._by_slug[slug_key] = descriptor
        self._by_slug_version[(slug_key, descriptor.semantic_version)] = descriptor

    def _build_descriptor(self, tool: ToolRegistry) -> ToolDescriptor:
        return ToolDescriptor(
            id=tool.id,
            name=tool.name,
            stable_slug=tool.stable_slug,
            semantic_version=tool.semantic_version,
            module_path=tool.module_path,
            function_name=tool.function_name,
            description=tool.description,
            input_schema=tool.input_schema or {},
            output_schema=tool.output_schema or {},
            owning_team=tool.owning_team,
            authorization_scope=tool.authorization_scope,
            approval_mode=tool.approval_mode,
            cost_profile=ToolRegistry.normalize_cost_profile(tool.cost_profile),
        )

    def _load_from_db(self, reference: Any) -> Optional[ToolDescriptor]:
        with self._session_scope() as session:
            candidate: Optional[ToolRegistry] = None
            if isinstance(reference, UUID):
                candidate = session.query(ToolRegistry).filter(ToolRegistry.id == reference).one_or_none()
            else:
                text = str(reference)
                try:
                    ref_uuid = UUID(text)
                except (TypeError, ValueError):
                    ref_uuid = None
                if ref_uuid is not None:
                    candidate = session.query(ToolRegistry).filter(ToolRegistry.id == ref_uuid).one_or_none()
                if candidate is None:
                    candidate = (
                        session.query(ToolRegistry)
                        .filter(ToolRegistry.name == text)
                        .one_or_none()
                    )
                if candidate is None:
                    candidate = (
                        session.query(ToolRegistry)
                        .filter(ToolRegistry.function_name == text)
                        .one_or_none()
                    )
                if candidate is None and "." in text:
                    module_name, function_name = text.rsplit(".", 1)
                    candidate = (
                        session.query(ToolRegistry)
                        .filter(
                            ToolRegistry.module_path == module_name,
                            ToolRegistry.function_name == function_name,
                        )
                        .one_or_none()
                    )
                if candidate is None:
                    slug_reference = self._parse_slug_reference(text)
                    if slug_reference is not None:
                        slug_value, version_value = slug_reference
                        candidate = (
                            session.query(ToolRegistry)
                            .filter(
                                ToolRegistry.stable_slug == slug_value,
                                ToolRegistry.semantic_version == version_value,
                            )
                            .one_or_none()
                        )
                if candidate is None:
                    slug_text = text.strip().lower()
                    if slug_text:
                        matches: List[ToolRegistry] = (
                            session.query(ToolRegistry)
                            .filter(ToolRegistry.stable_slug == slug_text)
                            .all()
                        )
                        if matches:
                            candidate = max(
                                matches,
                                key=lambda item: self._version_key(item.semantic_version),
                            )
            if candidate is None:
                return None
            return self._build_descriptor(candidate)

    def get(self, reference: Any) -> ToolDescriptor:
        with self._lock:
            cached = self._lookup_cached(reference)
            if cached is not None:
                return cached
        descriptor = self._load_from_db(reference)
        if descriptor is None:
            raise LookupError(f"Tool '{reference}' is not registered")
        with self._lock:
            self._store_descriptor(descriptor)
        return descriptor

    def resolve_agent_tools(self, references: Sequence[Any]) -> List[ToolDescriptor]:
        descriptors: List[ToolDescriptor] = []
        missing: List[str] = []
        for reference in references:
            try:
                descriptors.append(self.get(reference))
            except LookupError:
                missing.append(str(reference))
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Agent references unknown tools: {joined}")
        return descriptors

    def reload(self) -> None:
        with self._lock:
            self._by_id.clear()
            self._by_name.clear()
            self._by_slug.clear()
            self._by_slug_version.clear()


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
        raw_tools = agent.tools
        tool_refs: Tuple[str, ...]
        if isinstance(raw_tools, (list, tuple, set)):
            collected = [str(item).strip() for item in raw_tools if str(item).strip()]
            tool_refs = tuple(collected)
        elif raw_tools:
            text = str(raw_tools).strip()
            tool_refs = (text,) if text else ()
        else:
            tool_refs = ()
        policies = AgentRegistry.normalize_access_policies(agent.access_policies)
        quotas = AgentRegistry.normalize_quota_limits(agent.quota_limits)
        memory = AgentRegistry.normalize_memory_pointers(agent.memory_pointers)
        approvals = AgentRegistry.normalize_approval_requirements(agent.approval_requirements)
        return AgentDescriptor(
            id=agent.id,
            name=agent.name,
            module_path=agent.module_path,
            factory_function=agent.factory_function,
            description=agent.description,
            config_schema=agent.config_schema or {},
            allowed_tools=tool_refs,
            model_identifier=agent.model_identifier,
            provider=agent.provider,
            system_prompt=agent.system_prompt,
            memory_pointers=tuple(memory),
            rollout_enabled=bool(agent.rollout_enabled),
            rollout_stage=agent.rollout_stage,
            access_policies=policies,
            quota_limits=quotas,
            approval_requirements=approvals,
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
_TOOL_MANAGER = ToolRegistryManager()


def get_workflow_manager() -> WorkflowManager:
    """Return the shared workflow manager singleton."""

    return _MANAGER


def get_tool_registry_manager() -> ToolRegistryManager:
    """Return the shared tool registry manager singleton."""

    return _TOOL_MANAGER
