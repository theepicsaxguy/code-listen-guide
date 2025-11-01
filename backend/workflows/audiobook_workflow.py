"""Audiobook workflow that executes database-driven workflow revisions."""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
import logging
import threading
import time
from collections.abc import Mapping, Sequence
from datetime import datetime
from importlib import import_module
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

import requests
from agent_framework import AgentExecutor, ChatMessage, Role, TextContent, WorkflowBuilder

from backend.api.events import emit_job_event
from backend.config import get_settings
from backend.tools.db_tools import (
    get_job_by_id,
    mark_job_status,
    persist_audio_parts,
    persist_outline,
    save_chapter_script,
)
from backend.utils.checkpointing import PostgresCheckpointStorage
from backend.workflows.dynamic_loader import (
    AgentDescriptor,
    RevisionDescriptor,
    StepDescriptor,
    ToolDescriptor,
    WorkflowManager,
    get_tool_registry_manager,
    get_workflow_manager,
)

settings = get_settings()
logger = logging.getLogger(__name__)


try:  # pragma: no cover - import guard
    from opentelemetry import metrics  # type: ignore
except Exception:  # pragma: no cover - environment without OpenTelemetry
    metrics = None  # type: ignore[assignment]


def _build_meter() -> Any:
    if metrics is None:  # pragma: no cover - OpenTelemetry not installed
        return None
    try:
        return metrics.get_meter(__name__)
    except Exception:  # pragma: no cover - meter provider misconfiguration
        logger.debug("OpenTelemetry meter unavailable", exc_info=True)
        return None


def _create_counter(meter: Any, name: str, *, description: str, unit: str) -> Any:
    if meter is None:
        return None
    try:
        return meter.create_counter(name, description=description, unit=unit)
    except Exception:  # pragma: no cover - instrumentation failure
        logger.debug("Failed to create counter %s", name, exc_info=True)
        return None


def _create_histogram(meter: Any, name: str, *, description: str, unit: str) -> Any:
    if meter is None:
        return None
    try:
        return meter.create_histogram(name, description=description, unit=unit)
    except Exception:  # pragma: no cover - instrumentation failure
        logger.debug("Failed to create histogram %s", name, exc_info=True)
        return None


def _safe_counter_add(counter: Any, value: int, *, attributes: Dict[str, Any]) -> bool:
    if counter is None:
        return False
    try:
        counter.add(value, attributes=attributes)
        return True
    except Exception:  # pragma: no cover - instrumentation failure
        logger.debug("Failed to emit counter metric", exc_info=True, extra={"metric": counter})
        return False


def _safe_histogram_record(histogram: Any, value: float, *, attributes: Dict[str, Any]) -> bool:
    if histogram is None:
        return False
    try:
        histogram.record(value, attributes=attributes)
        return True
    except Exception:  # pragma: no cover - instrumentation failure
        logger.debug("Failed to emit histogram metric", exc_info=True, extra={"metric": histogram})
        return False


_METER = _build_meter()
_TOOL_CALL_COUNTER = _create_counter(
    _METER,
    "workflow_tool_calls",
    description="Total tool calls executed by the audiobook workflow",
    unit="1",
)
_TOOL_CALL_FAILURE_COUNTER = _create_counter(
    _METER,
    "workflow_tool_call_failures",
    description="Tool calls that failed or were rejected",
    unit="1",
)
_TOOL_CALL_DURATION = _create_histogram(
    _METER,
    "workflow_tool_call_duration_ms",
    description="Duration of tool executions in milliseconds",
    unit="ms",
)


class _BillingClient:
    """Send billing usage records to the external billing service."""

    def __init__(self, endpoint: Optional[str]) -> None:
        self._endpoint = endpoint.rstrip("/") if endpoint else None
        self._lock = threading.RLock()

    def send(self, payload: Dict[str, Any]) -> None:
        if not self._endpoint:
            return
        with self._lock:
            try:
                response = requests.post(self._endpoint, json=payload, timeout=2)
                response.raise_for_status()
            except Exception:  # pragma: no cover - network failure
                logger.warning(
                    "Failed to deliver billing usage record",
                    extra={"endpoint": self._endpoint, "job_id": payload.get("job_id")},
                    exc_info=True,
                )


class _AuditEmitter:
    """Forward structured audit events to the observability pipeline."""

    def __init__(self, endpoint: Optional[str]) -> None:
        self._endpoint = endpoint.rstrip("/") if endpoint else None
        self._lock = threading.RLock()

    def emit(self, payload: Dict[str, Any]) -> None:
        logger.info("Workflow audit event", extra={"audit": payload})
        if not self._endpoint:
            return
        with self._lock:
            try:
                response = requests.post(self._endpoint, json=payload, timeout=2)
                response.raise_for_status()
            except Exception:  # pragma: no cover - network failure
                logger.warning(
                    "Failed to forward audit event",
                    extra={"endpoint": self._endpoint, "job_id": payload.get("job_id")},
                    exc_info=True,
                )


class AudiobookWorkflow:
    """Execute the audiobook workflow using dynamic workflow revisions."""

    def __init__(
        self,
        job_id: str,
        repo_url: str,
        depth_tier: str,
        *,
        workflow_manager: Optional[WorkflowManager] = None,
        revision_id: Optional[str] = None,
    ) -> None:
        self.job_id = job_id
        self.job_uuid = UUID(str(job_id))
        self.repo_url = repo_url
        self.depth_tier = depth_tier
        self.manager = workflow_manager or get_workflow_manager()
        self.tool_manager = get_tool_registry_manager()
        self.revision = self._load_revision(revision_id)
        self.job_context = self._build_job_context()
        self.state = self.manager.ensure_instance(
            job_id=self.job_uuid,
            revision=self.revision,
            job_context=self.job_context,
        )
        self.checkpoints = PostgresCheckpointStorage(workflow_id=job_id)
        self._state_lock = threading.RLock()
        self._step_lookup: Dict[str, UUID] = {step.name: step.id for step in self.revision.steps}
        self._agent_allowed_cache: Dict[UUID, set[str]] = {}
        self._billing_summary: Dict[str, Dict[str, Any]] = {}
        self._billing_client = _BillingClient(settings.billing_service_url)
        self._audit_emitter = _AuditEmitter(settings.observability_ingest_url)

    def _build_job_context(self) -> Dict[str, Any]:
        job_record = get_job_by_id(str(self.job_uuid))
        return {
            "id": str(self.job_uuid),
            "repo_url": self.repo_url,
            "depth_tier": self.depth_tier,
            "repo_name": getattr(job_record, "repo_name", None),
            "repo_owner": getattr(job_record, "repo_owner", None),
            "git_ref": getattr(job_record, "git_ref", "main"),
        }

    def _load_revision(self, revision_id: Optional[str]) -> RevisionDescriptor:
        if revision_id is not None:
            return self.manager.load_revision(UUID(str(revision_id)))
        return self.manager.get_current_revision("audiobook_generation")

    async def execute(self) -> Dict[str, Any]:
        mark_job_status(self.job_id, "running", "analysis")
        emit_job_event(self.job_id, {"stage": "analysis"})

        analysis_step = self._get_step("analysis")
        analysis_result = await self._run_analysis(analysis_step)
        self._record_step_output(analysis_step, analysis_result)
        self._update_instance(analysis_step)

        mark_job_status(self.job_id, "running", "outline")
        emit_job_event(self.job_id, {"stage": "outline_start"})

        outline_step = self._get_step("outline")
        outline_result = await self._run_outline(outline_step, analysis_result)
        self._record_step_output(outline_step, outline_result)
        self._update_instance(outline_step)

        persist_outline(self.job_id, outline_result.get("data", outline_result.get("text", {})))
        emit_job_event(self.job_id, {"stage": "approval_wait"})

        approval_step = self._get_step("approval")
        self._update_instance(approval_step, status="paused")
        mark_job_status(self.job_id, "waiting_approval", "outline")
        return {"outline": outline_result.get("data", outline_result.get("text"))}

    async def continue_after_approval(self, approved_outline: Dict[str, Any]) -> Dict[str, Any]:
        self.state = self.manager.get_instance_state(self.job_uuid)
        approval_step = self._get_step("approval")
        self._record_step_output(
            approval_step,
            {
                "data": approved_outline,
                "text": json.dumps(approved_outline, ensure_ascii=False),
            },
        )
        self._update_instance(approval_step, status="running")

        mark_job_status(self.job_id, "running", "scripting")
        emit_job_event(self.job_id, {"stage": "scripting", "total": len(approved_outline.get("chapters", []))})

        script_step = self._get_step("scripting")
        scripts = await self._run_scripting(script_step, approved_outline)
        self._record_step_output(script_step, {"data": scripts})
        self._update_instance(script_step)

        mark_job_status(self.job_id, "running", "audio")
        emit_job_event(self.job_id, {"stage": "audio", "total": len(scripts)})

        audio_step = self._get_step("audio")
        audio_urls = await self._run_audio(audio_step, scripts)
        persist_audio_parts(self.job_id, audio_urls)
        self._record_step_output(audio_step, {"data": audio_urls})
        self._update_instance(audio_step)

        mark_job_status(self.job_id, "running", "postprocess")
        emit_job_event(self.job_id, {"stage": "postprocess"})

        post_step = self._get_step("post_processing")
        final_payload = await self._run_postprocess(post_step, audio_urls, approved_outline)
        self._record_step_output(post_step, final_payload)
        self._update_instance(post_step, completed=True, status="completed")

        mark_job_status(self.job_id, "completed", "done")
        emit_job_event(self.job_id, {"stage": "done"})
        return {
            "deliverables": final_payload.get("text"),
            "chapters": len(approved_outline.get("chapters", [])),
        }

    def cancel(self) -> None:
        mark_job_status(self.job_id, "cancelled", "cancelled")
        emit_job_event(self.job_id, {"stage": "cancelled"})
        try:
            self._update_instance(None, status="cancelled")
        except ValueError:
            logger.debug("Workflow instance missing for job %s during cancel", self.job_id)

    async def _run_analysis(self, step: StepDescriptor) -> Dict[str, Any]:
        agent = await self._create_agent(step.agent, step_name=step.name)
        message = self._build_message(
            "Analyze the repository at {repo_url} (git ref: {git_ref}) and respond with JSON containing summary, key components, languages,"
            " complexity, and suggested focus areas.",
            context=self.job_context,
        )
        response = await self._run_agent(agent, message, enable_checkpoint=step.checkpoint_enabled)
        parsed = self._safe_json_loads(response)
        return {"text": response, "data": parsed}

    async def _run_outline(self, step: StepDescriptor, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        agent = await self._create_agent(step.agent, step_name=step.name)
        context = {
            **self.job_context,
            "analysis": analysis_result.get("data") or self._safe_json_loads(analysis_result.get("text")),
        }
        analysis_json = json.dumps(context.get("analysis", {}), ensure_ascii=False)
        prompt = (
            "Using the repository analysis below, draft a structured audiobook outline tailored to the {depth_tier} depth tier."
            " Provide chapters with titles, objectives, summaries, and estimated durations.\n\n"
            f"Analysis JSON:\n{analysis_json}"
        )
        message = self._build_message(prompt, context=context)
        response = await self._run_agent(agent, message, enable_checkpoint=step.checkpoint_enabled)
        parsed = self._safe_json_loads(response)
        return {"text": response, "data": parsed}

    async def _run_scripting(self, step: StepDescriptor, approved_outline: Dict[str, Any]) -> List[str]:
        chapters = approved_outline.get("chapters", [])
        analysis_state = self._state_output("analysis")
        analysis_summary = analysis_state.get("data") or self._safe_json_loads(analysis_state.get("text"))
        scripts: List[str] = [""] * len(chapters)
        tasks = []
        for index, chapter in enumerate(chapters, start=1):
            tasks.append(
                asyncio.create_task(
                    self._run_single_script(
                        step.agent,
                        chapter,
                        analysis_summary,
                        chapter_number=index,
                        result_index=index - 1,
                        step_name=step.name,
                    )
                )
            )
        if not tasks:
            return []
        completed = 0
        for future in asyncio.as_completed(tasks):
            script_text, result_index = await future
            scripts[result_index] = script_text
            completed += 1
            save_chapter_script(self.job_id, result_index + 1, script_text)
            emit_job_event(
                self.job_id,
                {"stage": "scripts", "completed": completed, "total": len(chapters)},
            )
        return scripts

    async def _run_single_script(
        self,
        agent_descriptor: Optional[AgentDescriptor],
        chapter: Dict[str, Any],
        analysis_summary: Any,
        *,
        chapter_number: int,
        result_index: int,
        step_name: str,
    ) -> tuple[str, int]:
        agent = await self._create_agent(
            agent_descriptor,
            step_name=step_name,
            chapter_ctx=chapter,
        )
        context = {
            "chapter": chapter,
            "analysis": analysis_summary,
            "depth_tier": self.depth_tier,
            "chapter_number": chapter_number,
        }
        chapter_title = chapter.get("title") or f"Chapter {chapter_number}"
        prompt = (
            f"Write an engaging narration script for chapter {chapter_number} titled '{chapter_title}'."
            " Use the approved outline details and repository analysis."
            " Include transitions, learning objectives, and explanations of why the code is designed this way."
        )
        message = self._build_message(prompt, context=context)
        response = await self._run_agent(agent, message, enable_checkpoint=False)
        return response, result_index

    async def _run_audio(self, step: StepDescriptor, scripts: List[str]) -> List[str]:
        if not scripts:
            return []
        agent = await self._create_agent(step.agent, step_name=step.name)
        batch_size = int(step.step_config.get("batch_size", 5)) if step.step_config else 5
        audio_urls: List[str] = []
        for index in range(0, len(scripts), batch_size):
            batch = scripts[index : index + batch_size]
            prompt = "Generate high-quality narration audio for the provided scripts. Return an S3 URL for each part in order."
            message_text = f"{prompt}\n\n" + "\n\n".join(batch)
            message = ChatMessage(
                role=Role.USER,
                contents=[TextContent(text=message_text)],
            )
            response = await self._run_agent(
                agent,
                message,
                enable_checkpoint=step.checkpoint_enabled,
            )
            batch_urls = self._extract_audio_urls(response)
            audio_urls.extend(batch_urls)
            emit_job_event(
                self.job_id,
                {"stage": "audio", "completed": len(audio_urls), "total": len(scripts)},
            )
        return audio_urls

    async def _run_postprocess(
        self,
        step: StepDescriptor,
        audio_urls: List[str],
        outline: Dict[str, Any],
    ) -> Dict[str, Any]:
        agent = await self._create_agent(step.agent, step_name=step.name)
        context = {
            "audio_urls": audio_urls,
            "outline": outline,
            "job": self.job_context,
        }
        prompt = (
            "Assemble the final audiobook deliverables using the provided chapter audio URLs."
            " Return JSON with final bundle metadata, including download links and any additional resources."
        )
        message = self._build_message(prompt, context=context)
        response = await self._run_agent(
            agent,
            message,
            enable_checkpoint=step.checkpoint_enabled,
        )
        parsed = self._safe_json_loads(response)
        return {"text": response, "data": parsed}

    async def _create_agent(
        self,
        descriptor: Optional[AgentDescriptor],
        *,
        step_name: str,
        **factory_kwargs: Any,
    ) -> Any:
        if descriptor is None:
            raise ValueError("Step is missing an agent descriptor")
        module = import_module(descriptor.module_path)
        factory = getattr(module, descriptor.factory_function)
        call_kwargs = dict(factory_kwargs)
        runtime_tools = self._build_agent_tools(
            descriptor,
            step_name=step_name,
            context=dict(call_kwargs),
        )
        if runtime_tools is not None:
            call_kwargs["tools"] = runtime_tools
        metadata_payload = {
            "id": str(descriptor.id),
            "name": descriptor.name,
            "model_identifier": descriptor.model_identifier,
            "provider": descriptor.provider,
            "system_prompt": descriptor.system_prompt,
            "memory_pointers": list(descriptor.memory_pointers),
            "rollout_enabled": descriptor.rollout_enabled,
            "rollout_stage": descriptor.rollout_stage,
            "access_policies": descriptor.access_policies,
            "quota_limits": descriptor.quota_limits,
        }
        call_kwargs.setdefault("agent_metadata", metadata_payload)
        if descriptor.system_prompt and "system_prompt" not in call_kwargs:
            call_kwargs["system_prompt"] = descriptor.system_prompt
        if descriptor.memory_pointers and "memory_pointers" not in call_kwargs:
            call_kwargs["memory_pointers"] = list(descriptor.memory_pointers)
        if descriptor.model_identifier and "model_identifier" not in call_kwargs:
            call_kwargs["model_identifier"] = descriptor.model_identifier
        if descriptor.provider and "provider" not in call_kwargs:
            call_kwargs["provider"] = descriptor.provider
        if "quota_limits" not in call_kwargs:
            call_kwargs["quota_limits"] = descriptor.quota_limits
        if "access_policies" not in call_kwargs:
            call_kwargs["access_policies"] = descriptor.access_policies
        if "rollout_enabled" not in call_kwargs:
            call_kwargs["rollout_enabled"] = descriptor.rollout_enabled
        if descriptor.rollout_stage and "rollout_stage" not in call_kwargs:
            call_kwargs["rollout_stage"] = descriptor.rollout_stage
        agent = await factory(settings, **call_kwargs)
        return agent

    def _build_agent_tools(
        self,
        descriptor: AgentDescriptor,
        *,
        step_name: str,
        context: Mapping[str, Any],
    ) -> Optional[List[Callable[..., Any]]]:
        if not descriptor.allowed_tools:
            return None
        try:
            plugins = self.tool_manager.resolve_agent_tools(descriptor.allowed_tools)
        except ValueError as exc:
            raise RuntimeError(
                f"Agent '{descriptor.name}' references unknown tools"
            ) from exc
        if not plugins:
            return []
        wrappers: List[Callable[..., Any]] = []
        for plugin in plugins:
            wrappers.append(
                self._wrap_tool(
                    agent_descriptor=descriptor,
                    tool_descriptor=plugin,
                    step_name=step_name,
                    context=context,
                )
            )
        return wrappers

    def _wrap_tool(
        self,
        *,
        agent_descriptor: AgentDescriptor,
        tool_descriptor: ToolDescriptor,
        step_name: str,
        context: Mapping[str, Any],
    ) -> Callable[..., Any]:
        try:
            module = import_module(tool_descriptor.module_path)
            raw_function = getattr(module, tool_descriptor.function_name)
        except (ImportError, AttributeError) as exc:
            raise RuntimeError(
                f"Failed to load tool '{tool_descriptor.name}' from {tool_descriptor.module_path}"
            ) from exc

        signature = inspect.signature(raw_function)
        context_snapshot: Dict[str, Any] = {}
        job_context = self._coerce_jsonable(self.job_context)
        if job_context:
            context_snapshot["job"] = job_context
        factory_context = self._coerce_jsonable(context)
        if factory_context:
            context_snapshot["factory"] = factory_context
        agent_snapshot = {
            "id": str(agent_descriptor.id),
            "name": agent_descriptor.name,
            "model_identifier": agent_descriptor.model_identifier,
            "provider": agent_descriptor.provider,
            "system_prompt": agent_descriptor.system_prompt,
            "memory_pointers": list(agent_descriptor.memory_pointers),
            "rollout_enabled": agent_descriptor.rollout_enabled,
            "rollout_stage": agent_descriptor.rollout_stage,
            "access_policies": agent_descriptor.access_policies,
            "quota_limits": agent_descriptor.quota_limits,
        }
        context_snapshot["agent"] = agent_snapshot

        async def _async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.monotonic()
            trace = {
                "tool": tool_descriptor.name,
                "plugin_id": str(tool_descriptor.id),
                "agent_id": str(agent_descriptor.id),
                "agent_name": agent_descriptor.name,
                "step": step_name,
                "called_at": datetime.utcnow().isoformat(),
                "input": self._serialize_arguments(signature, args, kwargs),
            }
            if context_snapshot:
                trace["context"] = context_snapshot
            authorization = {
                "policy": "agent_tool_allow_list",
                "evaluated_at": datetime.utcnow().isoformat(),
            }
            try:
                self._validate_tool_authorization(agent_descriptor, tool_descriptor)
                authorization["allowed"] = True
                result = await raw_function(*args, **kwargs)
                trace["output"] = self._coerce_jsonable(result)
                duration = time.monotonic() - start
                self._finalize_tool_call(
                    trace,
                    status="ok",
                    duration=duration,
                    agent_descriptor=agent_descriptor,
                    tool_descriptor=tool_descriptor,
                    step_name=step_name,
                    authorization=authorization,
                    error=None,
                )
                return result
            except PermissionError as exc:
                trace["error"] = repr(exc)
                authorization["allowed"] = False
                authorization["reason"] = str(exc)
                duration = time.monotonic() - start
                self._finalize_tool_call(
                    trace,
                    status="forbidden",
                    duration=duration,
                    agent_descriptor=agent_descriptor,
                    tool_descriptor=tool_descriptor,
                    step_name=step_name,
                    authorization=authorization,
                    error=exc,
                )
                raise
            except Exception as exc:
                trace["error"] = repr(exc)
                if "allowed" not in authorization:
                    authorization["allowed"] = True
                authorization["reason"] = type(exc).__name__
                duration = time.monotonic() - start
                self._finalize_tool_call(
                    trace,
                    status="error",
                    duration=duration,
                    agent_descriptor=agent_descriptor,
                    tool_descriptor=tool_descriptor,
                    step_name=step_name,
                    authorization=authorization,
                    error=exc,
                )
                raise

        def _sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.monotonic()
            trace = {
                "tool": tool_descriptor.name,
                "plugin_id": str(tool_descriptor.id),
                "agent_id": str(agent_descriptor.id),
                "agent_name": agent_descriptor.name,
                "step": step_name,
                "called_at": datetime.utcnow().isoformat(),
                "input": self._serialize_arguments(signature, args, kwargs),
            }
            if context_snapshot:
                trace["context"] = context_snapshot
            authorization = {
                "policy": "agent_tool_allow_list",
                "evaluated_at": datetime.utcnow().isoformat(),
            }
            try:
                self._validate_tool_authorization(agent_descriptor, tool_descriptor)
                authorization["allowed"] = True
                result = raw_function(*args, **kwargs)
                trace["output"] = self._coerce_jsonable(result)
                duration = time.monotonic() - start
                self._finalize_tool_call(
                    trace,
                    status="ok",
                    duration=duration,
                    agent_descriptor=agent_descriptor,
                    tool_descriptor=tool_descriptor,
                    step_name=step_name,
                    authorization=authorization,
                    error=None,
                )
                return result
            except PermissionError as exc:
                trace["error"] = repr(exc)
                authorization["allowed"] = False
                authorization["reason"] = str(exc)
                duration = time.monotonic() - start
                self._finalize_tool_call(
                    trace,
                    status="forbidden",
                    duration=duration,
                    agent_descriptor=agent_descriptor,
                    tool_descriptor=tool_descriptor,
                    step_name=step_name,
                    authorization=authorization,
                    error=exc,
                )
                raise
            except Exception as exc:
                trace["error"] = repr(exc)
                if "allowed" not in authorization:
                    authorization["allowed"] = True
                authorization["reason"] = type(exc).__name__
                duration = time.monotonic() - start
                self._finalize_tool_call(
                    trace,
                    status="error",
                    duration=duration,
                    agent_descriptor=agent_descriptor,
                    tool_descriptor=tool_descriptor,
                    step_name=step_name,
                    authorization=authorization,
                    error=exc,
                )
                raise

        wrapper: Callable[..., Any]
        if asyncio.iscoroutinefunction(raw_function):
            async_wrapper = _async_wrapper
            functools.update_wrapper(async_wrapper, raw_function)
            async_wrapper.__name__ = tool_descriptor.name or raw_function.__name__
            async_wrapper.__doc__ = tool_descriptor.description or raw_function.__doc__
            async_wrapper.__signature__ = signature  # type: ignore[attr-defined]
            async_wrapper.__annotations__ = dict(getattr(raw_function, "__annotations__", {}))
            wrapper = async_wrapper
        else:
            sync_wrapper = _sync_wrapper
            functools.update_wrapper(sync_wrapper, raw_function)
            sync_wrapper.__name__ = tool_descriptor.name or raw_function.__name__
            sync_wrapper.__doc__ = tool_descriptor.description or raw_function.__doc__
            sync_wrapper.__signature__ = signature  # type: ignore[attr-defined]
            sync_wrapper.__annotations__ = dict(getattr(raw_function, "__annotations__", {}))
            wrapper = sync_wrapper

        setattr(wrapper, "__tool_descriptor__", tool_descriptor)
        setattr(wrapper, "__agent_descriptor__", agent_descriptor)
        return wrapper

    def _finalize_tool_call(
        self,
        trace: Dict[str, Any],
        *,
        status: str,
        duration: float,
        agent_descriptor: AgentDescriptor,
        tool_descriptor: ToolDescriptor,
        step_name: str,
        authorization: Dict[str, Any],
        error: Optional[BaseException],
    ) -> None:
        trace["status"] = status
        trace["duration_ms"] = round(duration * 1000, 3)
        if authorization:
            trace["authorization"] = authorization
        metric_attributes = {
            "job_id": self.job_id,
            "tool_id": str(tool_descriptor.id),
            "tool_name": tool_descriptor.name,
            "agent_id": str(agent_descriptor.id),
            "agent_name": agent_descriptor.name,
            "step": step_name,
            "status": status,
        }
        error_type = type(error).__name__ if error else None
        metrics_info = self._emit_tool_metrics(duration, metric_attributes, error_type)
        if metrics_info:
            trace["metrics"] = metrics_info
        cost_record = self._record_tool_cost(
            trace=trace,
            tool_descriptor=tool_descriptor,
            agent_descriptor=agent_descriptor,
            step_name=step_name,
            status=status,
            duration=duration,
        )
        if cost_record:
            trace["cost"] = cost_record
        self._append_tool_trace(step_name, trace)
        self._forward_audit_event(trace, metrics_info, cost_record)
        logger.info(
            "Tool %s executed for agent %s (step=%s) status=%s",
            tool_descriptor.name,
            agent_descriptor.name,
            step_name,
            status,
        )

    def _emit_tool_metrics(
        self,
        duration: float,
        attributes: Dict[str, Any],
        error_type: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        duration_ms = round(duration * 1000, 3)
        recorded = _safe_counter_add(_TOOL_CALL_COUNTER, 1, attributes=attributes)
        recorded = _safe_histogram_record(
            _TOOL_CALL_DURATION,
            duration_ms,
            attributes=attributes,
        ) or recorded
        metrics_info: Dict[str, Any] = {
            "status": attributes.get("status"),
            "duration_ms": duration_ms,
        }
        if attributes.get("status") != "ok":
            failure_attributes = dict(attributes)
            if error_type:
                failure_attributes["error_type"] = error_type
                metrics_info["error_type"] = error_type
            recorded = _safe_counter_add(
                _TOOL_CALL_FAILURE_COUNTER,
                1,
                attributes=failure_attributes,
            ) or recorded
        return metrics_info if recorded else None

    def _record_tool_cost(
        self,
        *,
        trace: Dict[str, Any],
        tool_descriptor: ToolDescriptor,
        agent_descriptor: AgentDescriptor,
        step_name: str,
        status: str,
        duration: float,
    ) -> Optional[Dict[str, Any]]:
        cost_profile = self._extract_cost_profile(tool_descriptor)
        tokens_used = self._extract_token_usage(trace)
        if not cost_profile and tokens_used is None:
            return None
        estimated_cost = self._estimate_cost(cost_profile, duration, tokens_used)
        if estimated_cost is None:
            estimated_cost = 0
        record: Dict[str, Any] = {
            "job_id": self.job_id,
            "tool_id": str(tool_descriptor.id),
            "tool_name": tool_descriptor.name,
            "agent_id": str(agent_descriptor.id),
            "agent_name": agent_descriptor.name,
            "step": step_name,
            "status": status,
            "recorded_at": datetime.utcnow().isoformat(),
            "estimated_cost_cents": int(estimated_cost),
        }
        if tokens_used is not None:
            record["tokens_used"] = int(tokens_used)
        provider = cost_profile.get("provider")
        if provider:
            record["provider"] = provider
        if cost_profile:
            record["cost_profile"] = self._coerce_jsonable(cost_profile)
        self._update_billing_summary(record)
        self._billing_client.send(record)
        return record

    def _forward_audit_event(
        self,
        trace: Dict[str, Any],
        metrics_info: Optional[Dict[str, Any]],
        cost_record: Optional[Dict[str, Any]],
    ) -> None:
        payload = {
            "job_id": self.job_id,
            "tool_id": trace.get("plugin_id"),
            "tool_name": trace.get("tool"),
            "agent_id": trace.get("agent_id"),
            "agent_name": trace.get("agent_name"),
            "step": trace.get("step"),
            "status": trace.get("status"),
            "authorization": trace.get("authorization"),
            "metrics": metrics_info,
            "cost": cost_record,
            "called_at": trace.get("called_at"),
        }
        self._audit_emitter.emit(payload)

    def _update_billing_summary(self, record: Dict[str, Any]) -> None:
        tool_id = record["tool_id"]
        with self._state_lock:
            summary = self._billing_summary.setdefault(
                tool_id,
                {
                    "tool_name": record.get("tool_name"),
                    "calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "estimated_cost_cents": 0,
                    "tokens_used": 0,
                },
            )
            summary["tool_name"] = record.get("tool_name") or summary.get("tool_name")
            summary["calls"] += 1
            if record.get("status") == "ok":
                summary["successful_calls"] += 1
            else:
                summary["failed_calls"] += 1
            summary["estimated_cost_cents"] += int(record.get("estimated_cost_cents", 0) or 0)
            if "tokens_used" in record:
                summary["tokens_used"] += int(record.get("tokens_used") or 0)
            if record.get("provider"):
                summary["provider"] = record["provider"]

    def _extract_cost_profile(self, descriptor: ToolDescriptor) -> Dict[str, Any]:
        profile: Dict[str, Any] = {}
        schemas = [descriptor.input_schema or {}, descriptor.output_schema or {}]
        for schema in schemas:
            if not isinstance(schema, Mapping):
                continue
            for candidate_key in ("metadata", "x-metadata", "x_metadata", "$metadata"):
                candidate = schema.get(candidate_key)
                if isinstance(candidate, Mapping):
                    self._merge_cost_metadata(profile, candidate)
            self._merge_cost_metadata(profile, schema)
        return {key: value for key, value in profile.items() if value is not None}

    def _merge_cost_metadata(self, target: Dict[str, Any], source: Mapping[str, Any]) -> None:
        numeric_keys = {
            "cost_per_call_cents": "cost_per_call_cents",
            "costPerCallCents": "cost_per_call_cents",
            "x-cost-per-call-cents": "cost_per_call_cents",
            "cost_per_1k_tokens_cents": "cost_per_1k_tokens_cents",
            "costPer1kTokensCents": "cost_per_1k_tokens_cents",
            "x-cost-per-1k-tokens-cents": "cost_per_1k_tokens_cents",
            "cost_per_second_cents": "cost_per_second_cents",
            "costPerSecondCents": "cost_per_second_cents",
            "estimated_tokens": "estimated_tokens",
            "estimatedTokens": "estimated_tokens",
        }
        passthrough_keys = {
            "provider": "provider",
            "currency": "currency",
            "billing_category": "billing_category",
            "usage_parameter": "usage_parameter",
        }
        for key, normalized in numeric_keys.items():
            if normalized in target:
                continue
            value = source.get(key)
            if value is not None:
                target[normalized] = value
        for key, normalized in passthrough_keys.items():
            if normalized in target:
                continue
            value = source.get(key)
            if value is not None:
                target[normalized] = value
        billing_block = source.get("billing")
        if isinstance(billing_block, Mapping):
            for key, value in billing_block.items():
                if value is None or key in target:
                    continue
                target[key] = value

    def _estimate_cost(
        self,
        profile: Mapping[str, Any],
        duration: float,
        tokens_used: Optional[int],
    ) -> Optional[int]:
        cost_per_call = self._to_number(profile.get("cost_per_call_cents"))
        if cost_per_call is not None:
            return int(round(cost_per_call))
        rate_per_tokens = self._to_number(profile.get("cost_per_1k_tokens_cents"))
        if rate_per_tokens is not None:
            token_count = tokens_used
            if token_count is None:
                token_count = self._to_int(profile.get("estimated_tokens"))
            if token_count is not None:
                return int(round((rate_per_tokens * token_count) / 1000))
        per_second = self._to_number(profile.get("cost_per_second_cents"))
        if per_second is not None:
            return int(round(per_second * duration))
        return None

    def _to_number(self, value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None

    def _to_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(round(value))
        if isinstance(value, str):
            try:
                return int(round(float(value)))
            except ValueError:
                return None
        return None

    def _extract_token_usage(self, trace: Mapping[str, Any]) -> Optional[int]:
        output = trace.get("output")
        return self._search_numeric(output, ("total_tokens", "tokens_used", "token_count", "tokens"))

    def _search_numeric(
        self,
        data: Any,
        keys: Sequence[str],
        depth: int = 0,
    ) -> Optional[int]:
        if depth > 5:
            return None
        if isinstance(data, Mapping):
            for key in keys:
                value = data.get(key)
                if isinstance(value, (int, float)):
                    return int(round(float(value)))
                if isinstance(value, str):
                    try:
                        return int(round(float(value)))
                    except ValueError:
                        continue
            for value in data.values():
                result = self._search_numeric(value, keys, depth + 1)
                if result is not None:
                    return result
        elif isinstance(data, Sequence) and not isinstance(data, (str, bytes, bytearray)):
            for item in data:
                result = self._search_numeric(item, keys, depth + 1)
                if result is not None:
                    return result
        return None

    def _append_tool_trace(self, step_name: str, trace: Dict[str, Any]) -> None:
        with self._state_lock:
            steps = self.state.setdefault("steps", {})
            step_state = steps.setdefault(step_name, {})
            tool_calls = step_state.setdefault("tool_calls", [])
            tool_calls.append(trace)
            step_state["updated_at"] = datetime.utcnow().isoformat()
            if self._billing_summary:
                billing_state = self.state.setdefault("billing_summary", {})
                billing_state["tools"] = json.loads(json.dumps(self._billing_summary))
                billing_state["updated_at"] = datetime.utcnow().isoformat()
            state_snapshot = json.loads(json.dumps(self.state))
        step_id = self._step_lookup.get(step_name)
        self.manager.update_instance(
            job_id=self.job_uuid,
            current_step_id=step_id,
            state=state_snapshot,
        )

    def _serialize_arguments(
        self,
        signature: inspect.Signature,
        args: Sequence[Any],
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            bound = signature.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            return {
                name: self._coerce_jsonable(value)
                for name, value in bound.arguments.items()
            }
        except TypeError:
            return {
                "args": self._coerce_jsonable(list(args)),
                "kwargs": self._coerce_jsonable(kwargs),
            }

    def _coerce_jsonable(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, Mapping):
            return {str(k): self._coerce_jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._coerce_jsonable(item) for item in value]
        if hasattr(value, "model_dump"):
            try:
                dumped = value.model_dump()
            except Exception:
                dumped = value.model_dump(mode="json", exclude_none=True)
            return self._coerce_jsonable(dumped)
        if hasattr(value, "__dict__"):
            return self._coerce_jsonable(vars(value))
        return repr(value)

    def _validate_tool_authorization(
        self,
        agent_descriptor: AgentDescriptor,
        tool_descriptor: ToolDescriptor,
    ) -> None:
        allowed = self._allowed_tokens(agent_descriptor)
        if not allowed:
            raise PermissionError(
                f"Agent '{agent_descriptor.name}' is not allowed to call any tools"
            )
        if "*" in allowed:
            return
        candidates = {
            tool_descriptor.name,
            tool_descriptor.name.lower(),
            tool_descriptor.function_name,
            tool_descriptor.function_name.lower(),
            tool_descriptor.module_path,
            tool_descriptor.module_path.lower(),
            f"{tool_descriptor.module_path}.{tool_descriptor.function_name}",
            f"{tool_descriptor.module_path}.{tool_descriptor.function_name}".lower(),
            str(tool_descriptor.id),
            str(tool_descriptor.id).lower(),
        }
        if allowed.isdisjoint(candidates):
            raise PermissionError(
                f"Agent '{agent_descriptor.name}' is not allowed to call tool '{tool_descriptor.name}'"
            )

    def _allowed_tokens(self, descriptor: AgentDescriptor) -> set[str]:
        cached = self._agent_allowed_cache.get(descriptor.id)
        if cached is not None:
            return cached
        tokens: set[str] = set()
        for reference in descriptor.allowed_tools:
            text = str(reference).strip()
            if not text:
                continue
            tokens.add(text)
            tokens.add(text.lower())
        self._agent_allowed_cache[descriptor.id] = tokens
        return tokens

    async def _run_agent(
        self,
        agent: Any,
        message: ChatMessage,
        *,
        enable_checkpoint: bool,
    ) -> str:
        executor = AgentExecutor(agent)
        builder = WorkflowBuilder().set_start_executor(executor)
        if enable_checkpoint:
            builder = builder.with_checkpointing(self.checkpoints)
        workflow = builder.build()
        final_text: Optional[str] = None
        async for event in workflow.run_stream(message):
            if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                final_text = event.message.text or final_text
        return final_text or ""

    def _build_message(self, prompt: str, *, context: Dict[str, Any]) -> ChatMessage:
        formatted_prompt = prompt.format(**{k: v for k, v in context.items() if isinstance(v, (str, int, float))})
        return ChatMessage(role=Role.USER, contents=[TextContent(text=formatted_prompt)])

    def _record_step_output(self, step: StepDescriptor, payload: Dict[str, Any]) -> None:
        with self._state_lock:
            steps = self.state.setdefault("steps", {})
            step_state = steps.setdefault(step.name, {})
            step_state["output"] = payload
            step_state["updated_at"] = datetime.utcnow().isoformat()

    def _update_instance(
        self,
        step: Optional[StepDescriptor],
        *,
        status: Optional[str] = None,
        completed: bool = False,
    ) -> None:
        step_id = step.id if step else None
        with self._state_lock:
            state_snapshot = json.loads(json.dumps(self.state))
        self.manager.update_instance(
            job_id=self.job_uuid,
            current_step_id=step_id,
            status=status,
            state=state_snapshot,
            completed=completed,
        )

    def _get_step(self, name: str) -> StepDescriptor:
        for step in self.revision.steps:
            if step.name == name:
                return step
        raise ValueError(f"Workflow revision missing required step '{name}'")

    def _safe_json_loads(self, payload: Optional[str]) -> Dict[str, Any]:
        if not payload:
            return {}
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _state_output(self, step_name: str) -> Dict[str, Any]:
        steps = self.state.get("steps", {})
        return steps.get(step_name, {}).get("output", {})

    def _extract_audio_urls(self, payload: str) -> List[str]:
        parsed = self._safe_json_loads(payload)
        if isinstance(parsed, dict) and "audio_files" in parsed:
            files = parsed.get("audio_files")
            if isinstance(files, list):
                return [str(item) for item in files]
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        segments = [segment.strip() for segment in payload.splitlines() if segment.strip()]
        return [segment for segment in segments if segment.startswith("http")]
