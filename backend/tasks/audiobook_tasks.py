"""
Integration points for the Microsoft Agent Framework audiobook workflow.

This module exposes thin async helpers that the FastAPI routes can call to
start or resume the multi-stage audiobook generation process.
"""

from backend.workflows.audiobook_workflow import AudiobookWorkflow


async def start_audiobook_workflow(job_id: str, repo_url: str, depth_tier: str) -> None:
    """
    Kick off the audiobook workflow for a job.

    TODO:
    1. Instantiate the chat client (Azure OpenAI or Anthropic)
    2. Create AudiobookWorkflow with checkpoint store
    3. Execute the workflow asynchronously
    4. Persist initial workflow status in the database
    5. Emit OpenTelemetry span for workflow start
    """

    raise NotImplementedError


async def resume_audiobook_workflow(job_id: str) -> None:
    """
    Resume a paused or failed workflow from its latest checkpoint.

    TODO:
    1. Load checkpoint metadata from PostgreSQL
    2. Rehydrate AudiobookWorkflow from saved state
    3. Call resume() on the workflow instance
    4. Update job status and progress indicators
    5. Emit OpenTelemetry span for workflow resume
    """

    raise NotImplementedError
