import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

try:
    from agent_framework import CheckpointStorage
except ImportError:

    class CheckpointStorage:
        async def save_checkpoint(self, step_id: str, state: Dict[str, Any]) -> str:
            raise RuntimeError("agent-framework package is required for checkpointing")

        async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
            raise RuntimeError("agent-framework package is required for checkpointing")

        async def list_checkpoints(self) -> List[Dict[str, Any]]:
            raise RuntimeError("agent-framework package is required for checkpointing")

        async def list_checkpoint_ids(self) -> List[str]:
            raise RuntimeError("agent-framework package is required for checkpointing")

        async def delete_checkpoint(self, checkpoint_id: str) -> bool:
            raise RuntimeError("agent-framework package is required for checkpointing")


from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.workflow_checkpoint import WorkflowCheckpoint


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

    async def save_checkpoint(self, step_id: str, state: Dict[str, Any]) -> str:
        checkpoint_id = str(uuid.uuid4())
        with self._session_scope() as db:
            record = WorkflowCheckpoint(
                id=checkpoint_id,
                workflow_id=self.workflow_id,
                step_id=step_id,
                state=state,
            )
            db.add(record)
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise
        return checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        with self._session_scope() as db:
            record = db.get(WorkflowCheckpoint, checkpoint_id)
            if record is None:
                return None
            return {
                "id": record.id,
                "workflow_id": record.workflow_id,
                "step_id": record.step_id,
                "state": record.state,
                "created_at": (
                    record.created_at.isoformat() if record.created_at else None
                ),
            }

    async def list_checkpoints(self) -> List[Dict[str, Any]]:
        with self._session_scope() as db:
            rows = (
                db.query(WorkflowCheckpoint)
                .filter(WorkflowCheckpoint.workflow_id == self.workflow_id)
                .order_by(WorkflowCheckpoint.created_at.asc())
                .all()
            )
            return [
                {
                    "id": row.id,
                    "step_id": row.step_id,
                    "state": row.state,
                    "created_at": (
                        row.created_at.isoformat() if row.created_at else None
                    ),
                }
                for row in rows
            ]

    async def list_checkpoint_ids(self) -> List[str]:
        with self._session_scope() as db:
            rows = (
                db.query(WorkflowCheckpoint.id)
                .filter(WorkflowCheckpoint.workflow_id == self.workflow_id)
                .order_by(WorkflowCheckpoint.created_at.asc())
                .all()
            )
            return [row[0] for row in rows]

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        with self._session_scope() as db:
            record = db.get(WorkflowCheckpoint, checkpoint_id)
            if record is None:
                return False
            db.delete(record)
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise
            return True


async def save_checkpoint(
    workflow_id: str,
    step_id: str,
    state: Dict[str, Any],
    *,
    session: Optional[Session] = None,
) -> str:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    return await storage.save_checkpoint(step_id, state)


async def load_checkpoint(
    workflow_id: str,
    checkpoint_id: str,
    *,
    session: Optional[Session] = None,
) -> Optional[Dict[str, Any]]:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    return await storage.load_checkpoint(checkpoint_id)


async def list_checkpoints(
    workflow_id: str, *, session: Optional[Session] = None
) -> List[Dict[str, Any]]:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    return await storage.list_checkpoints()


async def list_checkpoint_ids(
    workflow_id: str, *, session: Optional[Session] = None
) -> List[str]:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    return await storage.list_checkpoint_ids()


async def delete_checkpoint(
    workflow_id: str,
    checkpoint_id: str,
    *,
    session: Optional[Session] = None,
) -> bool:
    storage = PostgresCheckpointStorage(workflow_id, session=session)
    return await storage.delete_checkpoint(checkpoint_id)
