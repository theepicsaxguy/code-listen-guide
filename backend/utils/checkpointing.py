import uuid
from typing import Any, Dict, List, Optional

from agent_framework import CheckpointStorage
from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.workflow_checkpoint import WorkflowCheckpoint


class PostgresCheckpointStorage(CheckpointStorage):
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id

    def _session(self) -> Session:
        return SessionLocal()

    async def save_checkpoint(self, step_id: str, state: Dict[str, Any]) -> str:
        checkpoint_id = str(uuid.uuid4())
        with self._session() as db:
            record = WorkflowCheckpoint(
                id=checkpoint_id,
                workflow_id=self.workflow_id,
                step_id=step_id,
                state=state,
            )
            db.add(record)
            db.commit()
        return checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        with self._session() as db:
            record = db.get(WorkflowCheckpoint, checkpoint_id)
            if record is None:
                return None
            return {
                "id": record.id,
                "workflow_id": record.workflow_id,
                "step_id": record.step_id,
                "state": record.state,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            }

    async def list_checkpoints(self) -> List[Dict[str, Any]]:
        with self._session() as db:
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
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ]

    async def list_checkpoint_ids(self) -> List[str]:
        with self._session() as db:
            rows = (
                db.query(WorkflowCheckpoint.id)
                .filter(WorkflowCheckpoint.workflow_id == self.workflow_id)
                .order_by(WorkflowCheckpoint.created_at.asc())
                .all()
            )
            return [row[0] for row in rows]

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        with self._session() as db:
            record = db.get(WorkflowCheckpoint, checkpoint_id)
            if record is None:
                return False
            db.delete(record)
            db.commit()
            return True
