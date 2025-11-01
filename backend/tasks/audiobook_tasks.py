"""Task entry points for starting and resuming audiobook workflows."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable

from opentelemetry import trace

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


def _run_coroutine(coro: Awaitable[Any]) -> None:
    """Execute the provided coroutine in a new event loop."""

    asyncio.run(coro)


async def _start_audiobook_workflow(
    job_id: str, repo_url: str, depth_tier: str
) -> None:
    with tracer.start_as_current_span(
        "start_audiobook_workflow", attributes={"job_id": job_id}
    ):
        try:
            workflow = _create_workflow(
                job_id=job_id, repo_url=repo_url, depth_tier=depth_tier
            )
        except ValueError as exc:
            logger.warning(
                "Skipping workflow start for job %s: %s", job_id, exc
            )
            return
        await workflow.execute()


def start_audiobook_workflow(job_id: str, repo_url: str, depth_tier: str) -> None:
    """Kick off the audiobook workflow using a synchronous entry point."""

    _run_coroutine(_start_audiobook_workflow(job_id, repo_url, depth_tier))


async def _resume_audiobook_workflow(job_id: str) -> None:
    with tracer.start_as_current_span(
        "resume_audiobook_workflow", attributes={"job_id": job_id}
    ):
        job = _get_job(job_id)
        if job is None:
            logger.warning("Job %s not found when attempting resume", job_id)
            return
        try:
            workflow = _create_workflow(
                job_id=job_id, repo_url=job.repo_url, depth_tier=job.depth_tier
            )
        except ValueError as exc:
            logger.warning(
                "Skipping workflow resume for job %s: %s", job_id, exc
            )
            return
        outline_record = _load_outline(job_id)
        if outline_record is None:
            await workflow.execute()
            return
        outline_payload: Any = outline_record.outline_data
        if isinstance(outline_payload, str):
            outline_payload = json.loads(outline_payload)
        await workflow.continue_after_approval(outline_payload)


def resume_audiobook_workflow(job_id: str) -> None:
    """Resume a workflow from its latest checkpoint using a synchronous entry point."""

    _run_coroutine(_resume_audiobook_workflow(job_id))


def _create_workflow(job_id: str, repo_url: str, depth_tier: str):
    from backend.workflows.audiobook_workflow import AudiobookWorkflow

    return AudiobookWorkflow(job_id=job_id, repo_url=repo_url, depth_tier=depth_tier)


def _get_job(job_id: str):
    from backend.tools.db_tools import get_job_by_id

    return get_job_by_id(job_id)


def _load_outline(job_id: str):
    from backend.tools.db_tools import load_approved_outline

    return load_approved_outline(job_id)
