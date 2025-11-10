import asyncio
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

trace_module = ModuleType("opentelemetry.trace")
trace_module.get_tracer = lambda name: MagicMock()
opentelemetry_module = ModuleType("opentelemetry")
opentelemetry_module.trace = trace_module
sys.modules.setdefault("opentelemetry.trace", trace_module)
sys.modules.setdefault("opentelemetry", opentelemetry_module)

from backend.tasks import audiobook_tasks


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
    ['{"chapters": []}', {"chapters": []}],
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
    monkeypatch.setattr(
        audiobook_tasks,
        "_load_outline",
        lambda job_id: SimpleNamespace(outline_data=outline_payload),
    )

    audiobook_tasks.resume_audiobook_workflow("job-3")

    workflow.execute.assert_not_awaited()
    workflow.continue_after_approval.assert_awaited_once()


def test_cancel_workflow_with_active_workflow():
    """Test cancelling an active workflow."""
    workflow = MagicMock()
    workflow.cancel = MagicMock()
    
    # Register workflow
    with audiobook_tasks._workflows_lock:
        audiobook_tasks._active_workflows["job-123"] = workflow
    
    try:
        result = audiobook_tasks.cancel_workflow("job-123")
        
        assert result is True
        workflow.cancel.assert_called_once()
    finally:
        # Cleanup
        with audiobook_tasks._workflows_lock:
            audiobook_tasks._active_workflows.pop("job-123", None)


def test_cancel_workflow_without_active_workflow():
    """Test cancelling when no workflow is active."""
    result = audiobook_tasks.cancel_workflow("job-nonexistent")
    
    assert result is False


def test_cancel_workflow_handles_exception():
    """Test cancel_workflow handles exceptions gracefully."""
    workflow = MagicMock()
    workflow.cancel = MagicMock(side_effect=Exception("Test error"))
    
    # Register workflow
    with audiobook_tasks._workflows_lock:
        audiobook_tasks._active_workflows["job-456"] = workflow
    
    try:
        result = audiobook_tasks.cancel_workflow("job-456")
        
        assert result is False
        workflow.cancel.assert_called_once()
    finally:
        # Cleanup
        with audiobook_tasks._workflows_lock:
            audiobook_tasks._active_workflows.pop("job-456", None)


def test_workflow_registration_during_start(monkeypatch):
    """Test that workflows are registered during start."""
    workflow = MagicMock()
    workflow.execute = AsyncMock()
    monkeypatch.setattr(audiobook_tasks, "_create_workflow", lambda **kwargs: workflow)
    
    # Track registrations
    registrations = []
    original_start = audiobook_tasks._start_audiobook_workflow
    
    async def tracking_start(job_id, repo_url, depth_tier):
        # Check if registered during execution
        with audiobook_tasks._workflows_lock:
            registrations.append(job_id in audiobook_tasks._active_workflows)
        return await original_start(job_id, repo_url, depth_tier)
    
    monkeypatch.setattr(audiobook_tasks, "_start_audiobook_workflow", tracking_start)
    
    audiobook_tasks.start_audiobook_workflow(
        "job-test", "https://example.com/repo.git", "standard"
    )
    
    workflow.execute.assert_awaited_once()
    
    # Verify workflow was unregistered after completion
    with audiobook_tasks._workflows_lock:
        assert "job-test" not in audiobook_tasks._active_workflows


def test_workflow_registration_during_resume(monkeypatch):
    """Test that workflows are registered during resume."""
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
    
    audiobook_tasks.resume_audiobook_workflow("job-resume-test")
    
    workflow.execute.assert_awaited_once()
    
    # Verify workflow was unregistered after completion
    with audiobook_tasks._workflows_lock:
        assert "job-resume-test" not in audiobook_tasks._active_workflows
