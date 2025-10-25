import asyncio
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.models.agent_responses import OutlineAgentResponse
from backend.tasks import audiobook_tasks


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

trace_module = ModuleType("opentelemetry.trace")
trace_module.get_tracer = lambda name: MagicMock()
opentelemetry_module = ModuleType("opentelemetry")
opentelemetry_module.trace = trace_module
sys.modules.setdefault("opentelemetry.trace", trace_module)
sys.modules.setdefault("opentelemetry", opentelemetry_module)


def run_coroutine(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture(autouse=True)
def patch_runner(monkeypatch):
    monkeypatch.setattr(audiobook_tasks, "_run_coroutine", run_coroutine)


def test_start_audiobook_workflow_executes(monkeypatch):
    workflow = MagicMock()
    workflow.execute = AsyncMock()
    monkeypatch.setattr(audiobook_tasks, "_create_workflow", lambda **kwargs: workflow)

    audiobook_tasks.start_audiobook_workflow(
        "job-1", "https://example.com/repo.git", "standard"
    )

    workflow.execute.assert_awaited_once()


def test_resume_workflow_without_outline_runs_execute(monkeypatch):
    workflow = MagicMock()
    workflow.execute = AsyncMock()
    workflow.continue_after_approval = AsyncMock()
    monkeypatch.setattr(audiobook_tasks, "_create_workflow", lambda **kwargs: workflow)
    monkeypatch.setattr(
        audiobook_tasks,
        "_get_job",
        lambda job_id: SimpleNamespace(
            id=job_id, repo_url="https://example.com/repo.git", depth_tier="survey"
        ),
    )
    monkeypatch.setattr(audiobook_tasks, "_load_outline", lambda job_id: None)

    audiobook_tasks.resume_audiobook_workflow("job-2")

    workflow.execute.assert_awaited_once()
    workflow.continue_after_approval.assert_not_awaited()


@pytest.mark.parametrize(
    "outline_payload",
    [
        OutlineAgentResponse(chapters=[]),
        {"chapters": []},
        '{"chapters": []}',
    ],
)
def test_resume_workflow_with_outline_runs_continue(monkeypatch, outline_payload):
    workflow = MagicMock()
    workflow.execute = AsyncMock()
    workflow.continue_after_approval = AsyncMock()
    monkeypatch.setattr(audiobook_tasks, "_create_workflow", lambda **kwargs: workflow)
    monkeypatch.setattr(
        audiobook_tasks,
        "_get_job",
        lambda job_id: SimpleNamespace(
            id=job_id, repo_url="https://example.com/repo.git", depth_tier="survey"
        ),
    )
    stored_payload = (
        outline_payload.model_dump(mode="json")
        if isinstance(outline_payload, OutlineAgentResponse)
        else outline_payload
    )
    monkeypatch.setattr(
        audiobook_tasks,
        "_load_outline",
        lambda job_id: SimpleNamespace(outline_data=stored_payload),
    )

    audiobook_tasks.resume_audiobook_workflow("job-3")

    workflow.execute.assert_not_awaited()
    workflow.continue_after_approval.assert_awaited_once()
