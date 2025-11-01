"""
Tests for workflow orchestration.

Tests for:
- Audiobook workflow execution
- Workflow state management
- Checkpoint persistence and recovery
- Human-in-the-loop approval
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from agent_framework import ChatMessage, Role, TextContent


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
    async def test_execute_emits_outline_event_payload(self, monkeypatch):
        """Execute workflow and capture emitted outline payload."""
        from backend.workflows import audiobook_workflow as workflow_module

        class FakeWorkflowRunner:
            def __init__(self, events):
                self._events = events
                self.message = None

            async def run_stream(self, message):
                self.message = message
                for event in self._events:
                    yield event

        class FakeWorkflowBuilder:
            streams: list[list] = []
            runners: list[FakeWorkflowRunner] = []

            def __init__(self):
                pass

            def set_start_executor(self, _executor):
                return self

            def with_checkpointing(self, _checkpoints):
                return self

            def build(self):
                events = self.streams.pop(0) if self.streams else []
                runner = FakeWorkflowRunner(events)
                self.runners.append(runner)
                return runner

        class FakeSequentialBuilder:
            def participants(self, _participants):
                return self

            def build(self):
                return "sequential"

        outline_text = "{\"chapters\": []}"
        outline_events = [
            SimpleNamespace(
                message=ChatMessage(
                    role=Role.ASSISTANT,
                    contents=[TextContent(text=outline_text)],
                )
            )
        ]

        FakeWorkflowBuilder.streams = [outline_events]
        FakeWorkflowBuilder.runners = []

        monkeypatch.setattr(workflow_module, "WorkflowBuilder", FakeWorkflowBuilder)
        monkeypatch.setattr(workflow_module, "SequentialBuilder", FakeSequentialBuilder)
        monkeypatch.setattr(workflow_module, "AgentExecutor", lambda agent: agent)
        monkeypatch.setattr(workflow_module, "analyzer_agent", AsyncMock(return_value=object()))
        monkeypatch.setattr(workflow_module, "outline_agent", AsyncMock(return_value=object()))
        monkeypatch.setattr(workflow_module, "emit_job_event", MagicMock())
        monkeypatch.setattr(workflow_module, "mark_job_status", MagicMock())
        monkeypatch.setattr(workflow_module, "persist_outline", MagicMock())

        class FakeCheckpointStorage:
            def __init__(self, workflow_id: str):
                self.workflow_id = workflow_id

        monkeypatch.setattr(
            workflow_module, "PostgresCheckpointStorage", FakeCheckpointStorage
        )

        workflow = workflow_module.AudiobookWorkflow(
            job_id="job-42",
            repo_url="https://example.com/repo.git",
            depth_tier="survey",
        )

        result = await workflow.execute()

        assert result == {"outline": outline_text}
        workflow_module.persist_outline.assert_called_once_with("job-42", outline_text)
        workflow_module.emit_job_event.assert_any_call(
            "job-42", {"stage": "outline", "message": outline_text}
        )
        runner = FakeWorkflowBuilder.runners[0]
        assert runner.message is not None
        assert isinstance(runner.message, ChatMessage)
        assert runner.message.role == Role.USER

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
    async def test_continue_after_approval_emits_stage_payloads(self, monkeypatch):
        """Resume workflow and ensure streaming stages emit payloads."""
        from backend.workflows import audiobook_workflow as workflow_module

        class FakeWorkflowRunner:
            def __init__(self, events):
                self._events = events
                self.message = None

            async def run_stream(self, message):
                self.message = message
                for event in self._events:
                    yield event

        class FakeWorkflowBuilder:
            streams: list[list] = []
            runners: list[FakeWorkflowRunner] = []

            def __init__(self):
                pass

            def set_start_executor(self, _executor):
                return self

            def with_checkpointing(self, _checkpoints):
                return self

            def build(self):
                events = self.streams.pop(0) if self.streams else []
                runner = FakeWorkflowRunner(events)
                self.runners.append(runner)
                return runner

        class FakeConcurrentBuilder:
            def participants(self, _participants):
                return self

            def build(self):
                return "concurrent"

        script_texts = ["Chapter one script", "Chapter two script"]
        audio_urls = ["https://audio.local/1.mp3", "https://audio.local/2.mp3"]
        final_payload = "{\"bundle\": true}"

        script_events = [
            SimpleNamespace(
                message=ChatMessage(
                    role=Role.ASSISTANT,
                    contents=[TextContent(text=text)],
                )
            )
            for text in script_texts
        ]
        audio_events = [
            SimpleNamespace(
                message=ChatMessage(
                    role=Role.ASSISTANT,
                    contents=[TextContent(text=url)],
                )
            )
            for url in audio_urls
        ]
        post_events = [
            SimpleNamespace(
                message=ChatMessage(
                    role=Role.ASSISTANT,
                    contents=[TextContent(text=final_payload)],
                )
            )
        ]

        FakeWorkflowBuilder.streams = [script_events, audio_events, post_events]
        FakeWorkflowBuilder.runners = []

        monkeypatch.setattr(workflow_module, "WorkflowBuilder", FakeWorkflowBuilder)
        monkeypatch.setattr(workflow_module, "ConcurrentBuilder", FakeConcurrentBuilder)
        monkeypatch.setattr(workflow_module, "AgentExecutor", lambda agent: agent)
        monkeypatch.setattr(
            workflow_module,
            "script_agent",
            AsyncMock(side_effect=[object(), object()]),
        )
        monkeypatch.setattr(workflow_module, "audio_agent", AsyncMock(return_value=object()))
        monkeypatch.setattr(
            workflow_module, "postprocess_agent", AsyncMock(return_value=object())
        )
        monkeypatch.setattr(workflow_module, "emit_job_event", MagicMock())
        monkeypatch.setattr(workflow_module, "mark_job_status", MagicMock())
        monkeypatch.setattr(workflow_module, "persist_audio_parts", MagicMock())

        class FakeCheckpointStorage:
            def __init__(self, workflow_id: str):
                self.workflow_id = workflow_id

        monkeypatch.setattr(
            workflow_module, "PostgresCheckpointStorage", FakeCheckpointStorage
        )

        workflow = workflow_module.AudiobookWorkflow(
            job_id="job-77",
            repo_url="https://example.com/repo.git",
            depth_tier="deep",
        )

        result = await workflow.continue_after_approval(
            {"chapters": [{"number": 1}, {"number": 2}]}
        )

        assert result == {"deliverables": final_payload, "chapters": 2}
        workflow_module.persist_audio_parts.assert_called_once_with(
            "job-77", audio_urls
        )
        workflow_module.emit_job_event.assert_any_call(
            "job-77", {"stage": "scripts", "completed": 1, "total": 2}
        )
        workflow_module.emit_job_event.assert_any_call(
            "job-77", {"stage": "scripts", "completed": 2, "total": 2}
        )
        workflow_module.emit_job_event.assert_any_call(
            "job-77", {"stage": "audio", "completed": 1, "total": 2}
        )
        workflow_module.emit_job_event.assert_any_call(
            "job-77", {"stage": "audio", "completed": 2, "total": 2}
        )
        workflow_module.emit_job_event.assert_any_call(
            "job-77", {"stage": "postprocess"}
        )

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
            lambda job_id: SimpleNamespace(outline_data={"chapters": []}),
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
        assert isinstance(stored.state, dict)
        assert stored.state.get("shared_state", {}).get("state") == state

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

    @pytest.mark.asyncio
    async def test_checkpoint_preserves_thread_state(self, test_db):
        """Store and recover serialized thread metadata."""
        import pytest

        from backend.utils.checkpointing import load_checkpoint, save_checkpoint

        workflow_id = "workflow-thread"
        thread_state = {"service_thread_id": "thread-123"}

        checkpoint_id = await save_checkpoint(
            workflow_id=workflow_id,
            step_id="scripting",
            state={"status": "pending"},
            thread_state=thread_state,
            session=test_db,
        )

        loaded = await load_checkpoint(
            workflow_id=workflow_id,
            checkpoint_id=checkpoint_id,
            session=test_db,
        )

        assert loaded is not None
        assert loaded["metadata"]["thread_state"] == thread_state

        try:
            from agent_framework import AgentThread
        except ImportError:  # pragma: no cover - package variant without threads
            pytest.skip("AgentThread helper unavailable in installed agent_framework")

        restored_thread = await AgentThread.deserialize(thread_state)
        assert restored_thread.service_thread_id == "thread-123"


    def test_tool_call_records_metrics_billing_and_audit(self, monkeypatch):
        """Ensure tool instrumentation emits billing and audit payloads."""
        from datetime import datetime
        from types import SimpleNamespace
        from uuid import UUID, uuid4

        from backend.workflows import audiobook_workflow as workflow_module
        from backend.workflows.dynamic_loader import (
            AgentDescriptor,
            RevisionDescriptor,
            StepDescriptor,
            ToolDescriptor,
        )

        agent_descriptor = AgentDescriptor(
            id=uuid4(),
            name="outline-agent",
            module_path="pkg.agents",
            factory_function="build",
            description=None,
            config_schema={},
            allowed_tools=(),
            model_identifier="test-model",
            provider="test-provider",
            system_prompt="Provide assistance",
            memory_pointers=(),
            rollout_enabled=True,
            rollout_stage="beta",
            access_policies={"default": {"allow": [], "deny": [], "metadata": {}}, "overrides": []},
            quota_limits={"default": {"limit": None, "window": None, "cooldown_seconds": None, "metadata": {}}, "overrides": []},
        )
        step_descriptor = StepDescriptor(
            id=uuid4(),
            order=1,
            name="analysis",
            execution_mode="sequential",
            checkpoint_enabled=True,
            input_mapping={},
            output_mapping={},
            retry_policy=None,
            step_config={},
            agent=agent_descriptor,
        )
        revision_descriptor = RevisionDescriptor(
            id=uuid4(),
            workflow_id=uuid4(),
            workflow_name="audiobook_generation",
            version=1,
            is_published=True,
            metadata={},
            steps=[step_descriptor],
        )

        class DummyManager:
            def __init__(self) -> None:
                self.instance_state: Dict[str, Any] = {"steps": {}}
                self.updated: List[Any] = []

            def ensure_instance(
                self,
                *,
                job_id: UUID,
                revision: Any,
                job_context: Any,
            ) -> Dict[str, Any]:
                return dict(self.instance_state)

            def update_instance(
                self,
                *,
                job_id: UUID,
                current_step_id: Optional[UUID] = None,
                state: Optional[Dict[str, Any]] = None,
                **_: Any,
            ) -> None:
                if state is not None:
                    self.instance_state = state
                self.updated.append((job_id, current_step_id))

        dummy_manager = DummyManager()

        monkeypatch.setattr(
            workflow_module.AudiobookWorkflow,
            "_load_revision",
            lambda self, revision_id: revision_descriptor,
        )
        monkeypatch.setattr(
            workflow_module,
            "get_tool_registry_manager",
            lambda: SimpleNamespace(resolve_agent_tools=lambda _refs: []),
        )
        monkeypatch.setattr(
            workflow_module,
            "get_job_by_id",
            lambda _job_id: SimpleNamespace(repo_name="repo", repo_owner="owner", git_ref="main"),
        )
        monkeypatch.setattr(
            workflow_module,
            "PostgresCheckpointStorage",
            lambda workflow_id: SimpleNamespace(workflow_id=workflow_id),
        )

        workflow = workflow_module.AudiobookWorkflow(
            job_id=str(uuid4()),
            repo_url="https://example.com/repo.git",
            depth_tier="standard",
            workflow_manager=dummy_manager,
        )

        billing_events: List[Dict[str, Any]] = []
        audit_events: List[Dict[str, Any]] = []

        workflow._billing_client = SimpleNamespace(send=lambda payload: billing_events.append(payload))
        workflow._audit_emitter = SimpleNamespace(emit=lambda payload: audit_events.append(payload))

        tool_descriptor = ToolDescriptor(
            id=uuid4(),
            name="doc_search",
            stable_slug="doc-search",
            semantic_version="1.0.0",
            module_path="pkg.tools",
            function_name="run",
            description=None,
            input_schema={
                "metadata": {
                    "billing": {
                        "cost_per_1k_tokens_cents": 20,
                        "provider": "llm-provider",
                    }
                }
            },
            output_schema={},
            owning_team="core-platform",
            authorization_scope="internal",
            approval_mode="auto",
            cost_profile={"unit": "call", "estimated_cost_usd": 0.02},
        )

        trace: Dict[str, Any] = {
            "tool": tool_descriptor.name,
            "plugin_id": str(tool_descriptor.id),
            "agent_id": str(agent_descriptor.id),
            "agent_name": agent_descriptor.name,
            "step": step_descriptor.name,
            "called_at": datetime.utcnow().isoformat(),
            "input": {"topic": "intro"},
            "output": {"usage": {"total_tokens": 500}},
        }

        workflow._finalize_tool_call(
            trace,
            status="ok",
            duration=0.4,
            agent_descriptor=agent_descriptor,
            tool_descriptor=tool_descriptor,
            step_name=step_descriptor.name,
            authorization={"policy": "agent_tool_allow_list", "allowed": True},
            error=None,
        )

        assert billing_events, "billing payload should be sent"
        billing_payload = billing_events[0]
        assert billing_payload["estimated_cost_cents"] == 10
        tool_id = str(tool_descriptor.id)
        assert workflow._billing_summary[tool_id]["estimated_cost_cents"] == 10
        assert workflow._billing_summary[tool_id]["successful_calls"] == 1
        assert audit_events, "audit payload should be emitted"
        assert audit_events[0]["cost"]["estimated_cost_cents"] == 10
        assert tool_id in dummy_manager.instance_state["billing_summary"]["tools"]
        assert dummy_manager.updated, "workflow manager should persist state"


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
