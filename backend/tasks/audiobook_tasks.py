import json
from typing import Any

from opentelemetry import trace

from backend.tools.db_tools import get_job_by_id, load_approved_outline
from backend.workflows.audiobook_workflow import AudiobookWorkflow

tracer = trace.get_tracer(__name__)


async def start_audiobook_workflow(job_id: str, repo_url: str, depth_tier: str) -> None:
    with tracer.start_as_current_span("start_audiobook_workflow", attributes={"job_id": job_id}):
        workflow = AudiobookWorkflow(job_id=job_id, repo_url=repo_url, depth_tier=depth_tier)
        await workflow.execute()


async def resume_audiobook_workflow(job_id: str) -> None:
    with tracer.start_as_current_span("resume_audiobook_workflow", attributes={"job_id": job_id}):
        job = get_job_by_id(job_id)
        if job is None:
            return
        workflow = AudiobookWorkflow(job_id=job_id, repo_url=job.repo_url, depth_tier=job.depth_tier)
        outline_record = load_approved_outline(job_id)
        if outline_record is None:
            await workflow.execute()
            return
        outline_payload: Any = outline_record.outline_data
        if isinstance(outline_payload, str):
            outline_payload = json.loads(outline_payload)
        await workflow.continue_after_approval(outline_payload)
