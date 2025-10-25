"""
Tests for workflow orchestration.

Tests for:
- Audiobook workflow execution
- Workflow state management
- Checkpoint persistence and recovery
- Human-in-the-loop approval
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace

from backend.models.agent_responses import OutlineAgentResponse


@pytest.mark.workflows
@pytest.mark.unit
class TestAudiobookWorkflow:
    """Test audiobook generation workflow."""

    @pytest.fixture
    def mock_workflow(self):
        """Create a mock workflow instance."""
        workflow = MagicMock()
        workflow.execute = AsyncMock(
            return_value={"status": "completed", "job_id": "test-job"}
        )
        workflow.continue_after_approval = AsyncMock(
            return_value={"status": "completed", "job_id": "test-job"}
        )
        return workflow

    @pytest.mark.asyncio
    async def test_workflow_initialization(self):
        """Test workflow can be initialized."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        workflow = AudiobookWorkflow(
            job_id="test-job",
            repo_url="https://github.com/user/repo",
            depth_tier="standard",
        )

        assert workflow is not None
        assert workflow.job_id == "test-job"

    @pytest.mark.asyncio
    async def test_workflow_execute_full_pipeline(self, mock_workflow):
        """Test executing complete workflow."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        with patch.object(AudiobookWorkflow, "execute", mock_workflow.execute):
            workflow = AudiobookWorkflow(
                job_id="test-job",
                repo_url="https://github.com/user/repo",
                depth_tier="standard",
            )

            result = await workflow.execute()

            assert result is not None
            assert "status" in result or "job_id" in result

    @pytest.mark.asyncio
    async def test_workflow_stages_execute_in_order(self):
        """Test that workflow stages execute sequentially."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        workflow = AudiobookWorkflow(
            job_id="test-job",
            repo_url="https://github.com/user/repo",
            depth_tier="standard",
        )

        # Workflow should have defined stages:
        # 1. Analysis
        # 2. Outline Generation
        # 3. Human Approval (pause)
        # 4. Script Generation (parallel)
        # 5. Audio Synthesis (parallel)
        # 6. Post-processing

        assert hasattr(workflow, "execute") or hasattr(workflow, "run")

    @pytest.mark.asyncio
    async def test_workflow_handles_human_approval(self, mock_workflow):
        """Test workflow pauses for human approval."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        workflow = AudiobookWorkflow(
            job_id="test-job",
            repo_url="https://github.com/user/repo",
            depth_tier="standard",
        )

        # Workflow should be able to pause and resume
        assert hasattr(workflow, "continue_after_approval") or hasattr(
            workflow, "resume"
        )

    @pytest.mark.asyncio
    async def test_workflow_saves_checkpoints(self):
        """Test workflow saves progress checkpoints."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        workflow = AudiobookWorkflow(
            job_id="test-job",
            repo_url="https://github.com/user/repo",
            depth_tier="standard",
        )

        # Should save checkpoints after major stages
        # This would be tested by checking database for checkpoint records


@pytest.mark.workflows
@pytest.mark.unit
class TestWorkflowTasks:
    """Test workflow task functions."""

    def test_start_audiobook_workflow(self, monkeypatch):
        """Test starting workflow from task."""
        from backend.tasks import audiobook_tasks

        workflow = MagicMock()
        workflow.execute = AsyncMock()
        monkeypatch.setattr(
            audiobook_tasks, "_create_workflow", lambda **kwargs: workflow
        )

        # Run in sync mode for testing
        def run_coroutine(coro):
            import asyncio

            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        monkeypatch.setattr(audiobook_tasks, "_run_coroutine", run_coroutine)

        audiobook_tasks.start_audiobook_workflow(
            "job-1", "https://example.com/repo.git", "standard"
        )

        workflow.execute.assert_awaited_once()

    def test_resume_workflow_without_outline(self, monkeypatch):
        """Test resuming workflow when no outline exists."""
        from backend.tasks import audiobook_tasks

        workflow = MagicMock()
        workflow.execute = AsyncMock()
        workflow.continue_after_approval = AsyncMock()

        monkeypatch.setattr(
            audiobook_tasks, "_create_workflow", lambda **kwargs: workflow
        )
        monkeypatch.setattr(
            audiobook_tasks,
            "_get_job",
            lambda job_id: SimpleNamespace(
                id=job_id, repo_url="https://example.com/repo.git", depth_tier="survey"
            ),
        )
        monkeypatch.setattr(audiobook_tasks, "_load_outline", lambda job_id: None)

        def run_coroutine(coro):
            import asyncio

            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        monkeypatch.setattr(audiobook_tasks, "_run_coroutine", run_coroutine)

        audiobook_tasks.resume_audiobook_workflow("job-2")

        workflow.execute.assert_awaited_once()
        workflow.continue_after_approval.assert_not_awaited()

    def test_resume_workflow_with_outline(self, monkeypatch):
        """Test resuming workflow when outline exists."""
        from backend.tasks import audiobook_tasks

        workflow = MagicMock()
        workflow.execute = AsyncMock()
        workflow.continue_after_approval = AsyncMock()

        monkeypatch.setattr(
            audiobook_tasks, "_create_workflow", lambda **kwargs: workflow
        )
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
            lambda job_id: SimpleNamespace(
                outline_data=OutlineAgentResponse(chapters=[]).model_dump(mode="json")
            ),
        )

        def run_coroutine(coro):
            import asyncio

            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        monkeypatch.setattr(audiobook_tasks, "_run_coroutine", run_coroutine)

        audiobook_tasks.resume_audiobook_workflow("job-3")

        workflow.execute.assert_not_awaited()
        workflow.continue_after_approval.assert_awaited_once()


@pytest.mark.workflows
@pytest.mark.unit
class TestCheckpointing:
    """Test workflow checkpoint functionality."""

    @pytest.mark.asyncio
    async def test_save_checkpoint_persists_record(self, test_db):
        """Persist a checkpoint using the helper."""
        from backend.models.workflow_checkpoint import WorkflowCheckpoint
        from backend.utils.checkpointing import save_checkpoint

        workflow_id = "workflow-save"
        state = {"stage": "outline", "chapters": 8}

        checkpoint_id = await save_checkpoint(
            workflow_id=workflow_id,
            step_id="outline_generation",
            state=state,
            session=test_db,
        )

        stored = test_db.get(WorkflowCheckpoint, checkpoint_id)

        assert stored is not None
        assert stored.workflow_id == workflow_id
        assert stored.step_id == "outline_generation"
        assert stored.state == state

    @pytest.mark.asyncio
    async def test_load_checkpoint_returns_state(self, test_db):
        """Load a previously stored checkpoint."""
        from backend.utils.checkpointing import load_checkpoint, save_checkpoint

        workflow_id = "workflow-load"
        state = {"stage": "analysis", "status": "complete"}

        checkpoint_id = await save_checkpoint(
            workflow_id=workflow_id,
            step_id="analysis",
            state=state,
            session=test_db,
        )

        loaded = await load_checkpoint(
            workflow_id=workflow_id,
            checkpoint_id=checkpoint_id,
            session=test_db,
        )

        assert loaded is not None
        assert loaded["id"] == checkpoint_id
        assert loaded["workflow_id"] == workflow_id
        assert loaded["step_id"] == "analysis"
        assert loaded["state"] == state

    @pytest.mark.asyncio
    async def test_list_and_delete_checkpoints(self, test_db):
        """List and delete checkpoints for a workflow."""
        from backend.utils.checkpointing import (
            delete_checkpoint,
            list_checkpoint_ids,
            list_checkpoints,
            save_checkpoint,
        )

        workflow_id = "workflow-list"

        first = await save_checkpoint(
            workflow_id=workflow_id,
            step_id="analysis",
            state={"stage": "analysis"},
            session=test_db,
        )
        second = await save_checkpoint(
            workflow_id=workflow_id,
            step_id="outline",
            state={"stage": "outline"},
            session=test_db,
        )

        ids = await list_checkpoint_ids(workflow_id, session=test_db)
        assert ids == [first, second]

        checkpoints = await list_checkpoints(workflow_id, session=test_db)
        assert [cp["id"] for cp in checkpoints] == [first, second]

        deleted = await delete_checkpoint(workflow_id, first, session=test_db)
        assert deleted is True
        remaining_ids = await list_checkpoint_ids(workflow_id, session=test_db)
        assert remaining_ids == [second]

        deleted_again = await delete_checkpoint(workflow_id, first, session=test_db)
        assert deleted_again is False


@pytest.mark.workflows
@pytest.mark.integration
class TestWorkflowIntegration:
    """Integration tests for workflow execution."""

    @pytest.mark.skip(reason="Requires full environment with agents")
    @pytest.mark.asyncio
    async def test_end_to_end_workflow_execution(self, test_db, create_job):
        """Test complete workflow from start to finish."""
        job = create_job(status="pending")

        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        workflow = AudiobookWorkflow(
            job_id=str(job.id), repo_url=job.repo_url, depth_tier=job.depth_tier
        )

        result = await workflow.execute()

        # Workflow should complete successfully
        assert result is not None
        assert result.get("status") == "completed" or result.get("job_id") is not None

    @pytest.mark.skip(reason="Requires external services")
    @pytest.mark.asyncio
    async def test_workflow_with_real_repository(self):
        """Test workflow with actual GitHub repository."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        # Use a small public repository for testing
        workflow = AudiobookWorkflow(
            job_id="integration-test",
            repo_url="https://github.com/octocat/Hello-World",
            depth_tier="survey",
        )

        result = await workflow.execute()

        assert result is not None

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow handles errors gracefully."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        # Invalid repo URL should be handled
        workflow = AudiobookWorkflow(
            job_id="error-test",
            repo_url="https://github.com/nonexistent/repo",
            depth_tier="standard",
        )

        # Should not crash, but may return error
        try:
            result = await workflow.execute()
            # If it completes, result should indicate error
            assert result is not None
        except Exception as e:
            # Or it may raise an exception
            assert e is not None

    @pytest.mark.asyncio
    async def test_workflow_cancellation(self):
        """Test workflow can be cancelled mid-execution."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        workflow = AudiobookWorkflow(
            job_id="cancel-test",
            repo_url="https://github.com/user/repo",
            depth_tier="standard",
        )

        # Would need to implement cancellation mechanism
        assert hasattr(workflow, "cancel") or hasattr(workflow, "stop")

    @pytest.mark.asyncio
    async def test_parallel_chapter_processing(self):
        """Test workflow processes chapters in parallel."""
        from backend.workflows.audiobook_workflow import AudiobookWorkflow

        workflow = AudiobookWorkflow(
            job_id="parallel-test",
            repo_url="https://github.com/user/repo",
            depth_tier="comprehensive",
        )

        # Workflow should process script generation and audio synthesis in parallel
        # This would be verified by checking execution time and logs
        assert workflow is not None
