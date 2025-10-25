import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

try:
    from agent_framework import CheckpointStorage, WorkflowCheckpoint
except ImportError:

    class CheckpointStorage:  # type: ignore[override]
        async def save_checkpoint(self, checkpoint: "WorkflowCheckpoint") -> str:
            raise RuntimeError("agent-framework package is required for checkpointing")

        async def load_checkpoint(self, checkpoint_id: str) -> Optional["WorkflowCheckpoint"]:
            raise RuntimeError("agent-framework package is required for checkpointing")

        async def list_checkpoint_ids(
            self, workflow_id: Optional[str] = None
        ) -> List[str]:
            raise RuntimeError("agent-framework package is required for checkpointing")

        async def list_checkpoints(
            self, workflow_id: Optional[str] = None
        ) -> List["WorkflowCheckpoint"]:
            raise RuntimeError("agent-framework package is required for checkpointing")

        async def delete_checkpoint(self, checkpoint_id: str) -> bool:
            raise RuntimeError("agent-framework package is required for checkpointing")

    class WorkflowCheckpoint:  # type: ignore[override]
        def __init__(
            self,
            *,
            workflow_id: str,
            checkpoint_id: Optional[str] = None,
            messages: Optional[Dict[str, Any]] = None,
            shared_state: Optional[Dict[str, Any]] = None,
            executor_states: Optional[Dict[str, Dict[str, Any]]] = None,
            iteration_count: int = 0,
            max_iterations: int = 0,
            metadata: Optional[Dict[str, Any]] = None,
            timestamp: Optional[str] = None,
        ) -> None:
            import uuid

            self.checkpoint_id = checkpoint_id or str(uuid.uuid4())
            self.workflow_id = workflow_id
            self.messages = messages or {}
            self.shared_state = shared_state or {}
            self.executor_states = executor_states or {}
            self.iteration_count = iteration_count
            self.max_iterations = max_iterations
            self.metadata = metadata or {}
            self.timestamp = timestamp or ""

        def to_dict(self) -> Dict[str, Any]:
            return {
                "checkpoint_id": self.checkpoint_id,
                "workflow_id": self.workflow_id,
                "messages": self.messages,
                "shared_state": self.shared_state,
                "executor_states": self.executor_states,
                "iteration_count": self.iteration_count,
                "max_iterations": self.max_iterations,
                "metadata": self.metadata,
                "timestamp": self.timestamp,
            }

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "WorkflowCheckpoint":
            return cls(**data)


from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.workflow_checkpoint import (
    WorkflowCheckpoint as WorkflowCheckpointModel,
)


def _ensure_dict(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    return {}


class PostgresCheckpointStorage(CheckpointStorage):
    def __init__(self, workflow_id: str, *, session: Optional[Session] = None):
        self.workflow_id = workflow_id
        self._session = session

    @contextmanager
    def _session_scope(self) -> Iterator[Session]:
        if self._session is not None:
            yield self._session
            return
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> str:
        payload = checkpoint.to_dict()
        workflow_id = checkpoint.workflow_id or self.workflow_id
        metadata = _ensure_dict(payload.get("metadata"))
        step_label = metadata.get("step_id", "workflow")
        with self._session_scope() as db:
            record = WorkflowCheckpointModel(
                id=checkpoint.checkpoint_id,
                workflow_id=workflow_id,
                step_id=step_label,
                state=payload,
            )
            db.merge(record)
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise
        return checkpoint.checkpoint_id

    async def load_checkpoint(
        self, checkpoint_id: str
    ) -> Optional[WorkflowCheckpoint]:
        with self._session_scope() as db:
            record = db.get(WorkflowCheckpointModel, checkpoint_id)
            if record is None:
                return None
            payload = _ensure_dict(record.state)
            payload.setdefault("checkpoint_id", record.id)
            payload.setdefault("workflow_id", record.workflow_id)
            return WorkflowCheckpoint.from_dict(payload)

    async def list_checkpoint_ids(
        self, workflow_id: Optional[str] = None
    ) -> List[str]:
        with self._session_scope() as db:
            query = db.query(WorkflowCheckpointModel.id)
            target = workflow_id or self.workflow_id
            if target:
                query = query.filter(WorkflowCheckpointModel.workflow_id == target)
            rows = query.order_by(WorkflowCheckpointModel.created_at.asc()).all()
            return [row[0] for row in rows]

    async def list_checkpoints(
        self, workflow_id: Optional[str] = None
    ) -> List[WorkflowCheckpoint]:
        with self._session_scope() as db:
            query = db.query(WorkflowCheckpointModel)
            target = workflow_id or self.workflow_id
            if target:
                query = query.filter(WorkflowCheckpointModel.workflow_id == target)
            rows = query.order_by(WorkflowCheckpointModel.created_at.asc()).all()
            checkpoints: List[WorkflowCheckpoint] = []
            for row in rows:
                payload = _ensure_dict(row.state)
                payload.setdefault("checkpoint_id", row.id)
                payload.setdefault("workflow_id", row.workflow_id)
                checkpoints.append(WorkflowCheckpoint.from_dict(payload))
            return checkpoints

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        with self._session_scope() as db:
            record = db.get(WorkflowCheckpointModel, checkpoint_id)
            if record is None:
                return False
            db.delete(record)
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise
            return True


def _build_metadata(
    *,
    step_id: Optional[str],
    base: Optional[Dict[str, Any]],
    thread_state: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    if base:
        metadata.update(base)
    if step_id:
        metadata.setdefault("step_id", step_id)
    if thread_state:
        metadata["thread_state"] = thread_state
    return metadata


async def save_checkpoint(
    workflow_id: str,
    *,
    checkpoint: Optional[WorkflowCheckpoint] = None,
    step_id: Optional[str] = None,
    state: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    thread_state: Optional[Dict[str, Any]] = None,
    session: Optional[Session] = None,
) -> str:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    if checkpoint is None:
        payload_state = state or {}
        checkpoint = WorkflowCheckpoint(
            workflow_id=workflow_id,
            shared_state={"state": payload_state},
            metadata=_build_metadata(
                step_id=step_id, base=metadata, thread_state=thread_state
            ),
        )
    return await storage.save_checkpoint(checkpoint)


async def load_checkpoint(
    workflow_id: str,
    checkpoint_id: str,
    *,
    session: Optional[Session] = None,
) -> Optional[Dict[str, Any]]:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    checkpoint = await storage.load_checkpoint(checkpoint_id)
    if checkpoint is None:
        return None
    metadata = _ensure_dict(getattr(checkpoint, "metadata", {}))
    shared_state = _ensure_dict(getattr(checkpoint, "shared_state", {}))
    step_id = metadata.get("step_id", "workflow")
    state_payload = shared_state.get("state", shared_state)
    return {
        "id": checkpoint.checkpoint_id,
        "workflow_id": checkpoint.workflow_id or workflow_id,
        "step_id": step_id,
        "state": state_payload,
        "metadata": metadata,
        "shared_state": shared_state,
        "executor_states": getattr(checkpoint, "executor_states", {}),
        "raw_checkpoint": checkpoint,
    }


async def list_checkpoints(
    workflow_id: str, *, session: Optional[Session] = None
) -> List[Dict[str, Any]]:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    checkpoints = await storage.list_checkpoints(workflow_id)
    results: List[Dict[str, Any]] = []
    for checkpoint in checkpoints:
        metadata = _ensure_dict(getattr(checkpoint, "metadata", {}))
        shared_state = _ensure_dict(getattr(checkpoint, "shared_state", {}))
        state_payload = shared_state.get("state", shared_state)
        results.append(
            {
                "id": checkpoint.checkpoint_id,
                "workflow_id": checkpoint.workflow_id or workflow_id,
                "step_id": metadata.get("step_id", "workflow"),
                "state": state_payload,
                "metadata": metadata,
                "shared_state": shared_state,
                "executor_states": getattr(checkpoint, "executor_states", {}),
                "raw_checkpoint": checkpoint,
            }
        )
    return results


async def list_checkpoint_ids(
    workflow_id: str, *, session: Optional[Session] = None
) -> List[str]:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    return await storage.list_checkpoint_ids(workflow_id)


async def delete_checkpoint(
    workflow_id: str,
    checkpoint_id: str,
    *,
    session: Optional[Session] = None,
) -> bool:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    return await storage.delete_checkpoint(checkpoint_id)
