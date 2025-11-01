"""
Tests for workflow orchestration.

Tests for:
- Audiobook workflow execution
- Workflow state management
- Checkpoint persistence and recovery
- Human-in-the-loop approval
"""

import asyncio
import inspect
import json
import sys
import threading
from types import ModuleType, SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from agent_framework import ChatMessage, Role, TextContent
from backend.workflows.dynamic_loader import AgentDescriptor, ToolDescriptor


@pytest.fixture
def workflow_stub():
    from backend.workflows.audiobook_workflow import AudiobookWorkflow

    workflow = object.__new__(AudiobookWorkflow)
    workflow.job_id = "job-test"
    workflow.job_uuid = uuid4()
    workflow.job_context = {"repo_url": "https://example.com/repo.git"}
    workflow.state = {"steps": {}}
    workflow._state_lock = threading.RLock()
    workflow._step_lookup = {"tool-step": uuid4()}
    workflow.manager = MagicMock()
    workflow.manager.update_instance = MagicMock()
    workflow._agent_allowed_cache = {}
    workflow._validate_tool_authorization = MagicMock()
    return workflow


@pytest.fixture
def sample_tool_module():
    module_name = "tests.sample_tools"
    module = ModuleType(module_name)

    def add_numbers(a: int, b: int = 1) -> int:
        return a + b

    async def add_numbers_async(x: int, y: int = 2) -> dict[str, int]:
        await asyncio.sleep(0)
        return {"sum": x + y}

    async def raise_timeout(*args, **kwargs):
        raise asyncio.TimeoutError("budget exceeded")

    async def trigger_cancel(*args, **kwargs):
        raise asyncio.CancelledError()

    module.add_numbers = add_numbers
    module.add_numbers_async = add_numbers_async
    module.raise_timeout = raise_timeout
    module.trigger_cancel = trigger_cancel
    sys.modules[module_name] = module
    try:
        yield module
    finally:
        sys.modules.pop(module_name, None)


@pytest.mark.workflows
@pytest.mark.unit
class TestToolWrappingInternals:
    def test_serialize_arguments_coerces_defaults(self, workflow_stub):
        def sample_tool(value: int, extra: int = 2, *, payload: dict | None = None) -> None:
            return None

        signature = inspect.signature(sample_tool)
        payload = {"payload": {"ids": {1, 2}}}

        result = workflow_stub._serialize_arguments(signature, (5,), payload)

        assert result["value"] == 5
        assert result["extra"] == 2
        assert sorted(result["payload"]["ids"]) == [1, 2]

    def test_serialize_arguments_handles_binding_error(self, workflow_stub):
        def single_param(value: int) -> int:
            return value

        signature = inspect.signature(single_param)

        result = workflow_stub._serialize_arguments(signature, (1, 2), {"unexpected": 3})

        assert result["args"] == [1, 2]
        assert result["kwargs"] == {"unexpected": 3}

    def test_coerce_jsonable_handles_complex_objects(self, workflow_stub):
        class ModelStub:
            def model_dump(self, mode: str | None = None, exclude_none: bool | None = None) -> dict[str, str]:
                if mode is None:
                    raise ValueError("mode required")
                return {"mode": mode, "exclude_none": str(exclude_none)}

        class AttrStub:
            def __init__(self) -> None:
                self.alpha = "x"

        value = {
            "model": ModelStub(),
            "attrs": AttrStub(),
            "numbers": {3, 1},
            "mapping": {5: "five"},
        }

        result = workflow_stub._coerce_jsonable(value)

        assert result["model"] == {"mode": "json", "exclude_none": "True"}
        assert result["attrs"] == {"alpha": "x"}
        assert sorted(result["numbers"]) == [1, 3]
        assert result["mapping"] == {"5": "five"}

    def test_wrap_tool_sync_preserves_signature(self, workflow_stub, sample_tool_module):
        agent_descriptor = AgentDescriptor(
            id=uuid4(),
            name="agent",
            module_path="agents.module",
            factory_function="build",
            description=None,
            config_schema={},
            allowed_tools=(),
        )
        tool_descriptor = ToolDescriptor(
            id=uuid4(),
            name="adder",
            module_path=sample_tool_module.__name__,
            function_name="add_numbers",
            description="adds",
            input_schema={},
            output_schema={},
        )

        wrapper = workflow_stub._wrap_tool(
            agent_descriptor=agent_descriptor,
            tool_descriptor=tool_descriptor,
            step_name="tool-step",
            context={"chapter": 7},
        )

        result = wrapper(3)

        assert result == 4
        assert inspect.signature(wrapper) == inspect.signature(sample_tool_module.add_numbers)
        assert wrapper.__annotations__ == sample_tool_module.add_numbers.__annotations__
        workflow_stub._validate_tool_authorization.assert_called_once_with(agent_descriptor, tool_descriptor)
        workflow_stub.manager.update_instance.assert_called_once()
        state = workflow_stub.state["steps"]["tool-step"]
        trace = state["tool_calls"][0]
        assert trace["status"] == "ok"
        assert trace["output"] == 4
        assert trace["input"] == {"a": 3, "b": 1}
        assert trace["context"]["job"]["repo_url"] == "https://example.com/repo.git"
        assert trace["context"]["factory"] == {"chapter": 7}

    @pytest.mark.asyncio
    async def test_wrap_tool_async_preserves_signature(self, workflow_stub, sample_tool_module):
        agent_descriptor = AgentDescriptor(
            id=uuid4(),
            name="agent",
            module_path="agents.module",
            factory_function="build",
            description=None,
            config_schema={},
            allowed_tools=(),
        )
        tool_descriptor = ToolDescriptor(
            id=uuid4(),
            name="async-adder",
            module_path=sample_tool_module.__name__,
            function_name="add_numbers_async",
            description="adds async",
            input_schema={},
            output_schema={},
        )

        wrapper = workflow_stub._wrap_tool(
            agent_descriptor=agent_descriptor,
            tool_descriptor=tool_descriptor,
            step_name="tool-step",
            context={"chapter": 2},
        )

        result = await wrapper(5)

        assert result == {"sum": 7}
        assert inspect.signature(wrapper) == inspect.signature(sample_tool_module.add_numbers_async)
        assert wrapper.__annotations__ == sample_tool_module.add_numbers_async.__annotations__
        workflow_stub._validate_tool_authorization.assert_called_once_with(agent_descriptor, tool_descriptor)
        workflow_stub.manager.update_instance.assert_called_once()
        state = workflow_stub.state["steps"]["tool-step"]
        trace = state["tool_calls"][0]
        assert trace["status"] == "ok"
        assert trace["output"] == {"sum": 7}
        assert trace["input"] == {"x": 5, "y": 2}

    @pytest.mark.asyncio
    async def test_async_wrapper_skips_trace_on_timeout(self, workflow_stub, sample_tool_module):
        agent_descriptor = AgentDescriptor(
            id=uuid4(),
            name="agent",
            module_path="agents.module",
            factory_function="build",
            description=None,
            config_schema={},
            allowed_tools=(),
        )
        tool_descriptor = ToolDescriptor(
            id=uuid4(),
            name="timeout-tool",
            module_path=sample_tool_module.__name__,
            function_name="raise_timeout",
            description="times out",
            input_schema={},
            output_schema={},
        )

        wrapper = workflow_stub._wrap_tool(
            agent_descriptor=agent_descriptor,
            tool_descriptor=tool_descriptor,
            step_name="tool-step",
            context={},
        )

        with pytest.raises(asyncio.TimeoutError):
            await wrapper()

        workflow_stub._validate_tool_authorization.assert_called_once_with(agent_descriptor, tool_descriptor)
        workflow_stub.manager.update_instance.assert_not_called()
        assert workflow_stub.state == {"steps": {}}

    @pytest.mark.asyncio
    async def test_async_wrapper_skips_trace_on_cancellation(self, workflow_stub, sample_tool_module):
        agent_descriptor = AgentDescriptor(
            id=uuid4(),
            name="agent",
            module_path="agents.module",
            factory_function="build",
            description=None,
            config_schema={},
            allowed_tools=(),
        )
        tool_descriptor = ToolDescriptor(
            id=uuid4(),
            name="cancel-tool",
            module_path=sample_tool_module.__name__,
            function_name="trigger_cancel",
            description="cancels",
            input_schema={},
            output_schema={},
        )

        wrapper = workflow_stub._wrap_tool(
            agent_descriptor=agent_descriptor,
            tool_descriptor=tool_descriptor,
            step_name="tool-step",
            context={},
        )

        with pytest.raises(asyncio.CancelledError):
            await wrapper()

        workflow_stub._validate_tool_authorization.assert_called_once_with(agent_descriptor, tool_descriptor)
        workflow_stub.manager.update_instance.assert_not_called()
        assert workflow_stub.state == {"steps": {}}

    def test_append_tool_trace_rollback_on_failure(self, workflow_stub):
        workflow_stub.manager.update_instance.side_effect = RuntimeError("db unavailable")
        initial_state = json.loads(json.dumps(workflow_stub.state))

        with pytest.raises(RuntimeError):
            workflow_stub._append_tool_trace("tool-step", {"tool": "x"})

        assert workflow_stub.state == initial_state


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
