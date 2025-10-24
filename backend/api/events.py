import json
from typing import Any, Dict

from backend.api.ws import broadcast


def emit_job_event(job_id: str, payload: Dict[str, Any]) -> None:
    message = payload if isinstance(payload, str) else json.dumps(payload)
    broadcast(job_id, message)
