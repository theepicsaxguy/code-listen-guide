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
from agent_framework import (
    AgentExecutor,
    AgentRunEvent,
    AgentRunUpdateEvent,
    ChatMessage,
    FunctionCallContent,
    FunctionResultContent,
    Role,
    TextContent,
    WorkflowBuilder,
)
from agent_framework import AIFunction, AgentExecutor, ChatMessage, Role, TextContent, WorkflowBuilder

from backend.api.events import emit_job_event
from backend.config import get_settings
from backend.tools.db_tools import (
    get_job_by_id,
    mark_job_status,
    persist_audio_parts,
    persist_outline,
)
from backend.utils.checkpointing import PostgresCheckpointStorage
from backend.workflows.dynamic_loader import (
    AgentDescriptor,
    RevisionDescriptor,
    StepDescriptor,
    ToolDescriptor,
    ToolCostProfile,
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

_APPROVAL_MODE_ALIASES = {
    "auto": "never_require",
    "never": "never_require",
    "never_require": "never_require",
    "guarded": "always_require",
    "manual": "always_require",
    "always_require": "always_require",
}


def _map_tool_approval_mode(value: Optional[str]) -> str:
    normalized = (value or "auto").strip().lower()
    return _APPROVAL_MODE_ALIASES.get(normalized, "never_require")


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


class ToolAuthorizationError(PermissionError):
    """Raised when agent policy or quota checks reject a tool call."""

    def __init__(self, message: str, *, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.context = context or {}


class ToolApprovalRequiredError(ToolAuthorizationError):
    """Raised when a manual approval gate blocks tool execution."""


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
        self._tool_descriptor_cache: Dict[UUID, List[ToolDescriptor]] = {}
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
        prompt = (
            "Analyze the repository at {repo_url} (git ref: {git_ref}) and respond with JSON containing summary, key components, languages,"
            " complexity, and suggested focus areas."
        )
        message = self._build_message(prompt, context=self.job_context)
        response = await self._run_agent(
            agent,
            message,
            enable_checkpoint=step.checkpoint_enabled,
            step_name=step.name,
            agent_descriptor=step.agent,
            prompt_template=prompt,
        )
        parsed = self._safe_json_loads(response)
        return {"text": response, "data": parsed}

    async def _run_outline(self, step: StepDescriptor, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        descriptor = step.agent
        tool_descriptors = self._resolve_agent_tool_descriptors(descriptor) if descriptor else []
        agent = await self._create_agent(
            descriptor,
            step_name=step.name,
            tool_descriptors=tool_descriptors if descriptor else None,
        )
        context = {
            **self.job_context,
            "analysis": analysis_result.get("data")
            or self._safe_json_loads(analysis_result.get("text")),
        }
        prompt = (
            "Using the repository analysis, prepare a structured audiobook outline tailored to the "
            "{depth_tier} depth tier. Include chapter numbers, titles, objectives, summaries, "
            "and estimated durations. Respond with JSON compatible with the outline schema."
        )
        message = self._build_message(prompt, context=context)
        response = await self._run_agent(
        message = self._compose_agent_message(
            base_prompt=prompt,
            context=context,
            tool_descriptors=tool_descriptors,
        )
        response_text, _ = await self._run_agent_with_iterations(
            agent,
            message,
            enable_checkpoint=step.checkpoint_enabled,
            step_name=step.name,
            agent_descriptor=step.agent,
            prompt_template=prompt,
        )
        parsed = self._safe_json_loads(response)
        return {"text": response, "data": parsed}
        )
        parsed = self._safe_json_loads(response_text)
        return {"text": response_text, "data": parsed}

    async def _run_scripting(self, step: StepDescriptor, approved_outline: Dict[str, Any]) -> List[str]:
        chapters = approved_outline.get("chapters", [])
        analysis_state = self._state_output("analysis")
        analysis_summary = analysis_state.get("data") or self._safe_json_loads(analysis_state.get("text"))
        scripts: List[str] = [""] * len(chapters)
        tasks = []
        descriptor = step.agent
        tool_descriptors = self._resolve_agent_tool_descriptors(descriptor) if descriptor else []
        for index, chapter in enumerate(chapters, start=1):
            tasks.append(
                asyncio.create_task(
                    self._run_single_script(
                        step.agent,
                        chapter,
                        analysis_summary,
                        tool_descriptors=tool_descriptors,
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
        tool_descriptors: Sequence[ToolDescriptor],
        *,
        chapter_number: int,
        result_index: int,
        step_name: str,
    ) -> tuple[str, int]:
        if agent_descriptor is None:
            raise ValueError("Scripting step is missing an agent descriptor")
        agent = await self._create_agent(
            agent_descriptor,
            step_name=step_name,
            chapter_ctx=chapter,
            tool_descriptors=tool_descriptors if agent_descriptor else None,
        )
        context = {
            "chapter": chapter,
            "analysis": analysis_summary,
            "depth_tier": self.depth_tier,
            "chapter_number": chapter_number,
            "job_id": self.job_id,
        }
        chapter_title = chapter.get("title") or f"Chapter {chapter_number}"
        prompt = (
            f"Write an engaging narration script for chapter {chapter_number} titled '{chapter_title}'."
            " Use the approved outline details and repository analysis."
            " Include transitions, learning objectives, and explanations of why the code is designed this way."
            " Persist the finished script by calling the save_chapter_script tool with the correct job id and chapter number."
        )
        message = self._compose_agent_message(
            base_prompt=prompt,
            context=context,
            tool_descriptors=tool_descriptors,
        )
        message = self._build_message(prompt, context=context)
        response = await self._run_agent(
        response_text, _ = await self._run_agent_with_iterations(
            agent,
            message,
            enable_checkpoint=False,
            step_name=step_name,
            agent_descriptor=agent_descriptor,
            prompt_template=prompt,
        )
        return response, result_index
        )
        return response_text, result_index

    async def _run_audio(self, step: StepDescriptor, scripts: List[str]) -> List[str]:
        if not scripts:
            return []
        descriptor = step.agent
        tool_descriptors = self._resolve_agent_tool_descriptors(descriptor) if descriptor else []
        agent = await self._create_agent(
            descriptor,
            step_name=step.name,
            tool_descriptors=tool_descriptors if descriptor else None,
        )
        batch_size = int(step.step_config.get("batch_size", 5)) if step.step_config else 5
        audio_urls: List[str] = []
        for index in range(0, len(scripts), batch_size):
            batch = scripts[index : index + batch_size]
            context = {
                "job_id": self.job_id,
                "batch_start_index": index + 1,
                "scripts": batch,
                "total_scripts": len(scripts),
            }
            prompt = (
                "Turn each script in the batch into narrated audio. Use the synthesize_speech tool for text-to-speech "
                "and audio_upload_to_s3 (or equivalent) to publish the files. Provide the remote URLs in order."
            )
            message = self._compose_agent_message(
                base_prompt=prompt,
                context=context,
                tool_descriptors=tool_descriptors,
            )
            response_text, _ = await self._run_agent_with_iterations(
                agent,
                message,
                enable_checkpoint=step.checkpoint_enabled,
                step_name=step.name,
                agent_descriptor=step.agent,
                prompt_template=prompt,
            )
            batch_urls = self._extract_audio_urls(response_text)
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
        descriptor = step.agent
        tool_descriptors = self._resolve_agent_tool_descriptors(descriptor) if descriptor else []
        agent = await self._create_agent(
            descriptor,
            step_name=step.name,
            tool_descriptors=tool_descriptors if descriptor else None,
        )
        context = {
            "audio_urls": audio_urls,
            "outline": outline,
            "job": self.job_context,
        }
        prompt = (
            "Assemble the final audiobook deliverables from the chapter audio files. Merge chapters as needed, "
            "upload final assets, and return JSON describing every deliverable."
        )
        message = self._compose_agent_message(
            base_prompt=prompt,
            context=context,
            tool_descriptors=tool_descriptors,
        )
        response_text, _ = await self._run_agent_with_iterations(
            agent,
            message,
            enable_checkpoint=step.checkpoint_enabled,
            step_name=step.name,
            agent_descriptor=step.agent,
            prompt_template=prompt,
        )
        parsed = self._safe_json_loads(response_text)
        return {"text": response_text, "data": parsed}

    async def _create_agent(
        self,
        descriptor: Optional[AgentDescriptor],
        *,
        step_name: str,
        tool_descriptors: Optional[Sequence[ToolDescriptor]] = None,
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
            tool_descriptors=tool_descriptors,
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
            "approval_requirements": descriptor.approval_requirements,
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
        if "approval_requirements" not in call_kwargs:
            call_kwargs["approval_requirements"] = descriptor.approval_requirements
        if "rollout_enabled" not in call_kwargs:
            call_kwargs["rollout_enabled"] = descriptor.rollout_enabled
        if descriptor.rollout_stage and "rollout_stage" not in call_kwargs:
            call_kwargs["rollout_stage"] = descriptor.rollout_stage
        agent = await factory(settings, **call_kwargs)
        return agent

    def _resolve_agent_tool_descriptors(self, descriptor: AgentDescriptor) -> List[ToolDescriptor]:
        cached = self._tool_descriptor_cache.get(descriptor.id)
        if cached is not None:
            return cached
    def _build_agent_tools(
        self,
        descriptor: AgentDescriptor,
        *,
        step_name: str,
        context: Mapping[str, Any],
    ) -> Optional[List[AIFunction]]:
        if not descriptor.allowed_tools:
            self._tool_descriptor_cache[descriptor.id] = []
            return []
        try:
            plugins = self.tool_manager.resolve_agent_tools(descriptor.allowed_tools)
        except ValueError as exc:
            raise RuntimeError(
                f"Agent '{descriptor.name}' references unknown tools"
            ) from exc
        descriptors = list(plugins)
        self._tool_descriptor_cache[descriptor.id] = descriptors
        return descriptors

    def _build_agent_tools(
        self,
        descriptor: AgentDescriptor,
        *,
        step_name: str,
        context: Mapping[str, Any],
        tool_descriptors: Optional[Sequence[ToolDescriptor]] = None,
    ) -> Optional[List[Callable[..., Any]]]:
        plugins: Sequence[ToolDescriptor]
        if tool_descriptors is not None:
            plugins = list(tool_descriptors)
        else:
            if not descriptor.allowed_tools:
                return None
            plugins = self._resolve_agent_tool_descriptors(descriptor)
        if not plugins:
            return []
        wrappers: List[AIFunction] = []
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
    ) -> AIFunction:
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
            "approval_requirements": agent_descriptor.approval_requirements,
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
                "policy": "agent_access_controls",
                "evaluated_at": datetime.utcnow().isoformat(),
            }
            try:
                auth_context = self._validate_tool_authorization(
                    agent_descriptor,
                    tool_descriptor,
                )
                authorization.update(auth_context)
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
            except ToolAuthorizationError as exc:
                trace["error"] = repr(exc)
                authorization.update(getattr(exc, "context", {}))
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
                "policy": "agent_access_controls",
                "evaluated_at": datetime.utcnow().isoformat(),
            }
            try:
                auth_context = self._validate_tool_authorization(
                    agent_descriptor,
                    tool_descriptor,
                )
                authorization.update(auth_context)
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
            except ToolAuthorizationError as exc:
                trace["error"] = repr(exc)
                authorization.update(getattr(exc, "context", {}))
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

        additional_properties: Dict[str, Any] = {
            "tool_id": str(tool_descriptor.id),
            "stable_slug": tool_descriptor.stable_slug,
            "semantic_version": tool_descriptor.semantic_version,
            "authorization_scope": tool_descriptor.authorization_scope,
            "owning_team": tool_descriptor.owning_team,
            "cost_profile": tool_descriptor.cost_profile,
        }
        if tool_descriptor.output_schema:
            additional_properties["output_schema"] = tool_descriptor.output_schema

        input_schema = tool_descriptor.input_schema or None
        ai_tool = AIFunction(
            name=tool_descriptor.name or raw_function.__name__,
            description=tool_descriptor.description or raw_function.__doc__ or "",
            func=wrapper,
            input_model=input_schema,
            approval_mode=_map_tool_approval_mode(tool_descriptor.approval_mode),
            additional_properties=additional_properties,
        )
        setattr(ai_tool, "__tool_descriptor__", tool_descriptor)
        setattr(ai_tool, "__agent_descriptor__", agent_descriptor)
        setattr(ai_tool, "__wrapped__", wrapper)
        setattr(ai_tool, "__raw_function__", raw_function)
        return ai_tool

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
        if "type" not in trace:
            trace["type"] = "tool_call"
        trace.setdefault("tool_name", tool_descriptor.name)
        trace.setdefault("step", step_name)
        started_at = trace.get("called_at")
        if started_at:
            trace.setdefault("started_at", started_at)
        trace["completed_at"] = datetime.utcnow().isoformat()
        if "input" in trace:
            trace.setdefault("input_payload", trace.get("input"))
        if "output" in trace:
            trace.setdefault("output_payload", trace.get("output"))
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
        if not cost_profile.has_pricing() and tokens_used is None:
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
        if cost_profile.provider:
            record["provider"] = cost_profile.provider
        cost_payload = cost_profile.as_dict()
        if cost_payload:
            record["cost_profile"] = self._coerce_jsonable(cost_payload)
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

    def _estimate_cost(
        self,
        profile: ToolCostProfile,
        duration: float,
        tokens_used: Optional[int],
    ) -> Optional[int]:
        cost_per_call = self._to_number(profile.cost_per_call_cents)
        if cost_per_call is not None:
            return int(round(cost_per_call))
        rate_per_tokens = self._to_number(profile.cost_per_1k_tokens_cents)
        if rate_per_tokens is not None:
            token_count = tokens_used
            if token_count is None:
                token_count = self._to_int(profile.metadata.get("estimated_tokens"))
            if token_count is not None:
                return int(round((rate_per_tokens * token_count) / 1000))
        per_second = self._to_number(profile.cost_per_second_cents)
        if per_second is not None:
            return int(round(per_second * duration))
        return None

    def _extract_cost_profile(self, descriptor: ToolDescriptor) -> ToolCostProfile:
        return descriptor.cost_profile

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
        sanitized_trace = self._coerce_jsonable(trace)
        if "type" not in sanitized_trace:
            sanitized_trace["type"] = "tool_call"
        event_timestamp = (
            sanitized_trace.get("occurred_at")
            or sanitized_trace.get("called_at")
            or sanitized_trace.get("completed_at")
        )
        if event_timestamp and not isinstance(event_timestamp, str):
            try:
                event_timestamp = self._iso_timestamp(event_timestamp)
            except Exception:
                event_timestamp = None
        with self._state_lock:
            steps = self.state.setdefault("steps", {})
            step_state = steps.setdefault(step_name, {})
            tool_calls = step_state.setdefault("tool_calls", [])
            tool_calls.append(sanitized_trace)
            step_state["updated_at"] = event_timestamp or datetime.utcnow().isoformat()
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
    ) -> Dict[str, Any]:
        tokens = self._tool_tokens(tool_descriptor)
        allowed = self._allowed_tokens(agent_descriptor)
        if allowed and "*" not in allowed and allowed.isdisjoint(tokens):
            context = {
                "policy": {
                    "source": "allowed_tools",
                    "allowed_tokens": sorted(allowed),
                    "tool_tokens": sorted(tokens),
                }
            }
            raise ToolAuthorizationError(
                f"Agent '{agent_descriptor.name}' is not allowed to call tool '{tool_descriptor.name}'",
                context=context,
            )

        policy_context = self._evaluate_access_policies(
            agent_descriptor,
            tool_descriptor,
            tokens,
        )
        if not policy_context.get("allowed", True):
            raise ToolAuthorizationError(
                policy_context.get("message")
                or f"Agent '{agent_descriptor.name}' is not allowed to call tool '{tool_descriptor.name}'",
                context={"policy": policy_context},
            )

        quota_context = self._enforce_quota_limits(
            agent_descriptor,
            tool_descriptor,
            tokens,
        )
        approval_context = self._evaluate_tool_approval(
            agent_descriptor,
            tool_descriptor,
            tokens,
        )
        authorization: Dict[str, Any] = {
            "policy": policy_context,
        }
        if quota_context:
            authorization["quota"] = quota_context
        if approval_context:
            authorization["approval"] = approval_context
        return authorization

    def _allowed_tokens(self, descriptor: AgentDescriptor) -> set[str]:
        cached = self._agent_allowed_cache.get(descriptor.id)
        if cached is not None:
            return cached
        tokens: set[str] = set()
        for reference in descriptor.allowed_tools:
            text = str(reference).strip()
            if not text:
                continue
            tokens.add(text.lower())
        if "*" in tokens:
            tokens.add("*")
        self._agent_allowed_cache[descriptor.id] = tokens
        return tokens

    def _iso_timestamp(self, value: Any = None) -> str:
        if isinstance(value, str):
            return value
        if hasattr(value, "isoformat"):
            return value.isoformat()  # type: ignore[no-any-return]
        return datetime.utcnow().isoformat()

    def _agent_trace_event(
        self,
        *,
        agent_descriptor: AgentDescriptor,
        step_name: str,
        event_type: str,
        occurred_at: Any = None,
    ) -> Dict[str, Any]:
        return {
            "type": event_type,
            "agent_id": str(agent_descriptor.id),
            "agent_name": agent_descriptor.name,
            "step": step_name,
            "occurred_at": self._iso_timestamp(occurred_at),
        }

    def _record_agent_prompt_event(
        self,
        *,
        step_name: str,
        agent_descriptor: AgentDescriptor,
        message: ChatMessage,
        prompt_template: Optional[str],
    ) -> None:
        event = self._agent_trace_event(
            agent_descriptor=agent_descriptor,
            step_name=step_name,
            event_type="agent_prompt",
        )
        prompt_text = message.text.strip()
        if prompt_text:
            event["prompt_text"] = prompt_text
        serialized_message = self._coerce_jsonable(message.to_dict())
        if serialized_message:
            event["message"] = serialized_message
        if prompt_template:
            event["prompt_template"] = prompt_template
        system_prompt = agent_descriptor.system_prompt
        if system_prompt:
            event["system_prompt"] = system_prompt
        self._append_tool_trace(step_name, event)

    def _record_agent_update_event(
        self,
        *,
        step_name: str,
        agent_descriptor: AgentDescriptor,
        update: AgentRunUpdateEvent,
    ) -> Optional[str]:
        payload = update.data
        if payload is None:
            return None
        event = self._agent_trace_event(
            agent_descriptor=agent_descriptor,
            step_name=step_name,
            event_type="agent_update",
            occurred_at=getattr(payload, "created_at", None),
        )
        text = payload.text.strip() if payload.text else ""
        if text:
            event["text"] = text
        role = getattr(payload.role, "value", None) or getattr(payload, "role", None)
        if isinstance(role, Mapping):
            role = role.get("value")
        if isinstance(role, str) and role:
            event["role"] = role
        serialized = self._coerce_jsonable(payload.to_dict())
        if serialized:
            event["message"] = serialized
        self._append_tool_trace(step_name, event)
        return text or None

    def _record_agent_final_event(
        self,
        *,
        step_name: str,
        agent_descriptor: AgentDescriptor,
        run_event: AgentRunEvent,
    ) -> Optional[str]:
        response = run_event.data
        if response is None:
            return None
        event = self._agent_trace_event(
            agent_descriptor=agent_descriptor,
            step_name=step_name,
            event_type="agent_final",
            occurred_at=getattr(response, "created_at", None),
        )
        text = response.text.strip() if response.text else ""
        if text:
            event["text"] = text
        if response.response_id:
            event["response_id"] = response.response_id
        if response.value is not None:
            event["value"] = self._coerce_jsonable(response.value)
        messages = [self._coerce_jsonable(message.to_dict()) for message in response.messages]
        if messages:
            event["messages"] = messages
        usage = getattr(response, "usage_details", None)
        if usage is not None:
            if hasattr(usage, "to_dict"):
                usage = usage.to_dict()  # type: ignore[assignment]
            event["usage"] = self._coerce_jsonable(usage)
        additional = getattr(response, "additional_properties", None)
        if additional:
            event["metadata"] = self._coerce_jsonable(additional)
        self._append_tool_trace(step_name, event)
        return text or None
    def _tool_tokens(self, descriptor: ToolDescriptor) -> set[str]:
        tokens: set[str] = set()

        def add_token(value: Optional[str], prefix: Optional[str] = None) -> None:
            if not value:
                return
            text = str(value).strip()
            if not text:
                return
            tokens.add(text.lower())
            if prefix:
                tokens.add(f"{prefix}{text}".lower())

        add_token(descriptor.name)
        add_token(descriptor.function_name)
        add_token(descriptor.module_path)
        if descriptor.module_path and descriptor.function_name:
            add_token(f"{descriptor.module_path}.{descriptor.function_name}")
        add_token(descriptor.stable_slug)
        add_token(descriptor.stable_slug, prefix="tool:")
        add_token(descriptor.name, prefix="tool:")
        if descriptor.stable_slug and descriptor.semantic_version:
            add_token(f"{descriptor.stable_slug}@{descriptor.semantic_version}")
        add_token(str(descriptor.id))
        if descriptor.authorization_scope:
            add_token(descriptor.authorization_scope)
            add_token(descriptor.authorization_scope, prefix="scope:")
        if descriptor.owning_team:
            add_token(descriptor.owning_team)
            add_token(descriptor.owning_team, prefix="team:")
        if descriptor.approval_mode:
            add_token(descriptor.approval_mode)
            add_token(descriptor.approval_mode, prefix="approval:")
        return tokens

    def _evaluate_access_policies(
        self,
        agent_descriptor: AgentDescriptor,
        tool_descriptor: ToolDescriptor,
        tokens: set[str],
    ) -> Dict[str, Any]:
        policies = agent_descriptor.access_policies or {}
        overrides = list(policies.get("overrides") or [])
        applicable: List[tuple[str, Dict[str, Any]]] = []
        for rule in overrides:
            subject = str(rule.get("subject") or "").strip()
            if subject and subject.lower() not in tokens:
                continue
            label = subject or "override"
            applicable.append((label, rule))
        default_rule = policies.get("default") or {}
        applicable.append(("default", default_rule))

        decision: Dict[str, Any] = {
            "policy": "agent_access_policies",
            "tokens": sorted(tokens),
            "allowed": True,
            "rule": "default",
        }

        allow_rules: List[tuple[set[str], str, Dict[str, Any]]] = []
        for label, rule in applicable:
            metadata = rule.get("metadata") if isinstance(rule.get("metadata"), Mapping) else {}
            denies = {
                str(item).strip().lower()
                for item in rule.get("deny", [])
                if isinstance(item, (str, bytes)) or item
            }
            denies.discard("")
            if denies and not denies.isdisjoint(tokens):
                decision.update(
                    {
                        "allowed": False,
                        "rule": label,
                        "matched_deny": sorted(denies.intersection(tokens)),
                        "metadata": metadata,
                        "message": metadata.get("reason")
                        or f"Agent policy denies use of tool '{tool_descriptor.name}'",
                    }
                )
                return decision

            allows = {
                str(item).strip().lower()
                for item in rule.get("allow", [])
                if isinstance(item, (str, bytes)) or item
            }
            allows.discard("")
            if allows:
                allow_rules.append((allows, label, rule))

        if allow_rules:
            for allows, label, rule in allow_rules:
                metadata = rule.get("metadata") if isinstance(rule.get("metadata"), Mapping) else {}
                if not allows.isdisjoint(tokens):
                    decision.update(
                        {
                            "allowed": True,
                            "rule": label,
                            "matched_allow": sorted(allows.intersection(tokens)),
                            "metadata": metadata,
                        }
                    )
                    return decision
            allows, label, rule = allow_rules[0]
            metadata = rule.get("metadata") if isinstance(rule.get("metadata"), Mapping) else {}
            decision.update(
                {
                    "allowed": False,
                    "rule": label,
                    "expected_allow": sorted(allows),
                    "metadata": metadata,
                    "message": metadata.get("reason")
                    or f"Agent policy does not permit tool '{tool_descriptor.name}'",
                }
            )
            return decision

        metadata = default_rule.get("metadata") if isinstance(default_rule.get("metadata"), Mapping) else {}
        decision["metadata"] = metadata
        return decision

    def _quota_window_id(self, window: Optional[str], now: datetime) -> str:
        if not window:
            return "lifetime"
        normalized = window.strip().lower()
        if normalized == "daily":
            return f"daily:{now.date().isoformat()}"
        if normalized == "hourly":
            return now.strftime("hourly:%Y-%m-%dT%H")
        if normalized == "weekly":
            iso_year, iso_week, _ = now.isocalendar()
            return f"weekly:{iso_year}-W{iso_week:02d}"
        if normalized == "monthly":
            return now.strftime("monthly:%Y-%m")
        return f"{normalized}:{now.date().isoformat()}"

    def _parse_iso_timestamp(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def _touch_quota_record(
        self,
        agent_descriptor: AgentDescriptor,
        *,
        subject: Optional[str],
        window: Optional[str],
        now: datetime,
        increment: bool,
    ) -> Dict[str, Any]:
        key = (subject or "default").strip().lower() or "default"
        state_snapshot: Optional[Dict[str, Any]] = None
        with self._state_lock:
            quota_state = self.state.setdefault("quota_usage", {})
            agent_state = quota_state.setdefault(str(agent_descriptor.id), {})
            record = dict(agent_state.get(key) or {})
            window_id = self._quota_window_id(window, now)
            changed = False
            if record.get("window_id") != window_id:
                record = {
                    "window_id": window_id,
                    "window": window or None,
                    "count": 0,
                    "last_call_at": None,
                }
                changed = True
            count = int(record.get("count", 0) or 0)
            if increment:
                count += 1
                record["count"] = count
                record["last_call_at"] = now.isoformat()
                changed = True
            else:
                record["count"] = count
            if changed:
                record["updated_at"] = now.isoformat()
                agent_state[key] = record
                state_snapshot = json.loads(json.dumps(self.state))
        if state_snapshot is not None:
            self.manager.update_instance(
                job_id=self.job_uuid,
                state=state_snapshot,
            )
        last_call = self._parse_iso_timestamp(record.get("last_call_at"))
        return {
            "subject": subject or "default",
            "window": window or "lifetime",
            "window_id": record.get("window_id"),
            "count": int(record.get("count", 0) or 0),
            "last_call_at": last_call,
        }

    def _enforce_quota_limits(
        self,
        agent_descriptor: AgentDescriptor,
        tool_descriptor: ToolDescriptor,
        tokens: set[str],
    ) -> Dict[str, Any]:
        quotas = agent_descriptor.quota_limits or {}
        overrides = list(quotas.get("overrides") or [])
        now = datetime.utcnow()
        applicable: List[tuple[str, Dict[str, Any]]] = []
        for rule in overrides:
            subject = str(rule.get("subject") or "").strip()
            if subject and subject.lower() not in tokens:
                continue
            label = subject or "override"
            applicable.append((label, rule))
        default_rule = quotas.get("default") or {}
        applicable.append(("default", default_rule))

        enforced: List[tuple[str, Optional[str], Dict[str, Any], Optional[int], Optional[int]]] = []
        for label, rule in applicable:
            limit = self._to_int(rule.get("limit"))
            cooldown = self._to_int(rule.get("cooldown_seconds"))
            if limit is None and cooldown is None:
                continue
            subject = rule.get("subject") or label
            window_value = rule.get("window")
            window = (
                str(window_value).strip().lower()
                if isinstance(window_value, str)
                else None
            )
            metadata = rule.get("metadata") if isinstance(rule.get("metadata"), Mapping) else {}
            record = self._touch_quota_record(
                agent_descriptor,
                subject=subject,
                window=window,
                now=now,
                increment=False,
            )
            count = record.get("count", 0)
            last_call = record.get("last_call_at")
            if cooldown is not None and isinstance(last_call, datetime):
                elapsed = (now - last_call).total_seconds()
                if elapsed < cooldown:
                    remaining = int(max(round(cooldown - elapsed), 0))
                    context = {
                        "subject": record["subject"],
                        "window": record["window"],
                        "count": count,
                        "limit": limit,
                        "cooldown_seconds": cooldown,
                        "remaining_cooldown_seconds": remaining,
                        "metadata": metadata,
                    }
                    message = metadata.get("reason") or (
                        f"Tool '{tool_descriptor.name}' is cooling down for {remaining}s"
                    )
                    raise ToolAuthorizationError(message, context={"quota": context})
            if limit is not None and count >= limit:
                context = {
                    "subject": record["subject"],
                    "window": record["window"],
                    "count": count,
                    "limit": limit,
                    "cooldown_seconds": cooldown,
                    "metadata": metadata,
                }
                message = metadata.get("reason") or (
                    f"Tool '{tool_descriptor.name}' exceeded its {record['window']} quota"
                )
                raise ToolAuthorizationError(message, context={"quota": context})
            enforced.append((subject, window, metadata, limit, cooldown))

        if not enforced:
            return {}

        applied: List[Dict[str, Any]] = []
        for subject, window, metadata, limit, cooldown in enforced:
            record = self._touch_quota_record(
                agent_descriptor,
                subject=subject,
                window=window,
                now=now,
                increment=True,
            )
            applied.append(
                {
                    "subject": record["subject"],
                    "window": record["window"],
                    "count": record["count"],
                    "limit": limit,
                    "cooldown_seconds": cooldown,
                    "metadata": metadata,
                }
            )
        return {"applied": applied}

    def _resolve_approval_requirement(
        self,
        agent_descriptor: AgentDescriptor,
        tool_descriptor: ToolDescriptor,
        tokens: set[str],
    ) -> Dict[str, Any]:
        approvals = agent_descriptor.approval_requirements or {}
        overrides = list(approvals.get("overrides") or [])
        for rule in overrides:
            subject = str(rule.get("subject") or "").strip()
            if subject and subject.lower() not in tokens:
                continue
            metadata = rule.get("metadata") if isinstance(rule.get("metadata"), Mapping) else {}
            mode = str(rule.get("mode", "auto")).strip().lower() or "auto"
            return {
                "mode": mode,
                "rule": subject or "override",
                "metadata": metadata,
            }
        default_rule = approvals.get("default") or {}
        metadata = default_rule.get("metadata") if isinstance(default_rule.get("metadata"), Mapping) else {}
        mode = str(default_rule.get("mode", "auto")).strip().lower() or "auto"
        return {
            "mode": mode,
            "rule": "default",
            "metadata": metadata,
        }

    def _record_tool_approval_request(
        self,
        agent_descriptor: AgentDescriptor,
        tool_descriptor: ToolDescriptor,
        requirement: Dict[str, Any],
    ) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        request_id = f"{agent_descriptor.id}:{tool_descriptor.id}"
        reason = None
        metadata = requirement.get("metadata")
        if isinstance(metadata, Mapping):
            reason = metadata.get("reason")
        payload = {
            "id": request_id,
            "agent_id": str(agent_descriptor.id),
            "agent_name": agent_descriptor.name,
            "tool_id": str(tool_descriptor.id),
            "tool_name": tool_descriptor.name,
            "requested_at": now,
            "status": "pending",
            "requirement": requirement,
        }
        if reason:
            payload["reason"] = reason

        state_snapshot: Optional[Dict[str, Any]] = None
        with self._state_lock:
            approvals = self.state.setdefault("pending_tool_approvals", {})
            existing = approvals.get(request_id)
            if existing and existing.get("status") == "pending":
                payload = existing
            else:
                approvals[request_id] = payload
                state_snapshot = json.loads(json.dumps(self.state))
        if state_snapshot is not None:
            self.manager.update_instance(
                job_id=self.job_uuid,
                state=state_snapshot,
            )
            emit_job_event(
                self.job_id,
                {
                    "stage": "tool_approval_wait",
                    "agent_id": str(agent_descriptor.id),
                    "agent_name": agent_descriptor.name,
                    "tool_id": str(tool_descriptor.id),
                    "tool_name": tool_descriptor.name,
                    "reason": payload.get("reason"),
                },
            )
        return payload

    def _evaluate_tool_approval(
        self,
        agent_descriptor: AgentDescriptor,
        tool_descriptor: ToolDescriptor,
        tokens: set[str],
    ) -> Dict[str, Any]:
        requirement = self._resolve_approval_requirement(
            agent_descriptor,
            tool_descriptor,
            tokens,
        )
        mode_value = requirement.get("mode", "auto")
        mode = str(mode_value).strip().lower()
        tool_mode = str(tool_descriptor.approval_mode or "auto").strip().lower()
        requires_manual = mode in {"human", "manual", "guarded"} or tool_mode in {"manual", "guarded"}
        context = {
            "mode": mode,
            "rule": requirement.get("rule"),
            "metadata": requirement.get("metadata", {}),
            "tool_mode": tool_mode,
        }
        if not requires_manual:
            return context
        payload = self._record_tool_approval_request(
            agent_descriptor,
            tool_descriptor,
            requirement,
        )
        context["request"] = payload
        message = context["metadata"].get("reason") if isinstance(context["metadata"], Mapping) else None
        raise ToolApprovalRequiredError(
            message or f"Tool '{tool_descriptor.name}' requires human approval",
            context={"approval": context},
        )

    async def _run_agent(
        self,
        agent: Any,
        message: ChatMessage,
        *,
        enable_checkpoint: bool,
        step_name: str,
        agent_descriptor: AgentDescriptor,
        prompt_template: Optional[str],
    ) -> str:
        executor = AgentExecutor(agent)
        builder = WorkflowBuilder().set_start_executor(executor)
        if enable_checkpoint:
            builder = builder.with_checkpointing(self.checkpoints)
        workflow = builder.build()
        self._record_agent_prompt_event(
            step_name=step_name,
            agent_descriptor=agent_descriptor,
            message=message,
            prompt_template=prompt_template,
        )
        final_text: Optional[str] = None
        async for event in workflow.run_stream(message):
            if isinstance(event, AgentRunUpdateEvent):
                interim = self._record_agent_update_event(
                    step_name=step_name,
                    agent_descriptor=agent_descriptor,
                    update=event,
                )
                final_text = interim or final_text
                continue
            if isinstance(event, AgentRunEvent):
                result_text = self._record_agent_final_event(
                    step_name=step_name,
                    agent_descriptor=agent_descriptor,
                    run_event=event,
                )
                final_text = result_text or final_text
            if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                final_text = event.message.text or final_text
        return final_text or ""

    def _build_message(self, prompt: str, *, context: Dict[str, Any]) -> ChatMessage:
        formatted_prompt = prompt.format(**{k: v for k, v in context.items() if isinstance(v, (str, int, float))})
        return ChatMessage(role=Role.USER, contents=[TextContent(text=formatted_prompt)])

    def _compose_agent_message(
        self,
        *,
        base_prompt: str,
        context: Mapping[str, Any],
        tool_descriptors: Sequence[ToolDescriptor],
    ) -> ChatMessage:
        segments: List[str] = [base_prompt.strip()]
        json_context = json.dumps(self._coerce_jsonable(context), ensure_ascii=False, indent=2)
        segments.append("Context JSON:")
        segments.append(json_context)
        if tool_descriptors:
            segments.append("Available tools:")
            for descriptor in tool_descriptors:
                descriptor_block = {
                    "name": descriptor.name,
                    "description": descriptor.description,
                    "input_schema": descriptor.input_schema,
                    "output_schema": descriptor.output_schema,
                }
                segments.append(
                    json.dumps(
                        self._coerce_jsonable(descriptor_block),
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            segments.append(
                "Use the tools above when they help. Call them with precise arguments. "
                "When all required actions are finished, provide a clear final answer."
            )
        message_text = "\n\n".join(segment for segment in segments if segment)
        return ChatMessage(role=Role.USER, contents=[TextContent(text=message_text)])

    async def _run_agent_with_iterations(
        self,
        agent: Any,
        message: ChatMessage,
        *,
        enable_checkpoint: bool,
        step_name: str,
    ) -> tuple[str, List[Dict[str, Any]]]:
        executor = AgentExecutor(agent)
        builder = WorkflowBuilder().set_start_executor(executor)
        if enable_checkpoint:
            builder = builder.with_checkpointing(self.checkpoints)
        workflow = builder.build()
        final_text: Optional[str] = None
        pending_calls: Dict[str, Dict[str, Any]] = {}
        iterations: List[Dict[str, Any]] = []
        async for event in workflow.run_stream(message):
            if isinstance(event, AgentRunUpdateEvent):
                update = event.data
                if update is None:
                    continue
                self._ingest_agent_contents(update.contents, pending_calls, iterations)
                if update.text:
                    final_text = (final_text or "") + update.text
            elif isinstance(event, AgentRunEvent):
                response = event.data
                if response is None:
                    continue
                for msg in response.messages:
                    self._ingest_agent_contents(msg.contents, pending_calls, iterations)
                    if msg.role == Role.ASSISTANT:
                        text_payload = msg.text or ""
                        if not text_payload and msg.contents:
                            text_payload = "".join(
                                content.text
                                for content in msg.contents
                                if isinstance(content, TextContent)
                            )
                        if text_payload:
                            final_text = text_payload
        for remaining in pending_calls.values():
            iterations.append(remaining)
        if iterations:
            self._record_iteration_history(step_name, iterations)
        return final_text or "", iterations

    def _ingest_agent_contents(
        self,
        contents: Optional[Sequence[Any]],
        pending_calls: Dict[str, Dict[str, Any]],
        iterations: List[Dict[str, Any]],
    ) -> None:
        if not contents:
            return
        for content in contents:
            if isinstance(content, FunctionCallContent):
                entry = {
                    "call_id": content.call_id,
                    "tool": content.name,
                    "arguments": self._coerce_jsonable(content.parse_arguments() or {}),
                    "requested_at": datetime.utcnow().isoformat(),
                }
                if content.exception is not None:
                    entry["request_exception"] = repr(content.exception)
                pending_calls[content.call_id] = entry
            elif isinstance(content, FunctionResultContent):
                entry = pending_calls.pop(content.call_id, {"call_id": content.call_id})
                entry.setdefault("tool", getattr(content, "name", entry.get("tool")))
                entry["result"] = self._coerce_jsonable(content.result)
                entry["completed_at"] = datetime.utcnow().isoformat()
                if content.exception is not None:
                    entry["result_exception"] = repr(content.exception)
                iterations.append(entry)

    def _record_iteration_history(self, step_name: str, iterations: Sequence[Dict[str, Any]]) -> None:
        if not iterations:
            return
        serializable = [self._coerce_jsonable(entry) for entry in iterations]
        with self._state_lock:
            steps = self.state.setdefault("steps", {})
            step_state = steps.setdefault(step_name, {})
            history = step_state.setdefault("llm_iterations", [])
            history.extend(serializable)
            step_state["updated_at"] = datetime.utcnow().isoformat()
            state_snapshot = json.loads(json.dumps(self.state))
        step_id = self._step_lookup.get(step_name)
        self.manager.update_instance(
            job_id=self.job_uuid,
            current_step_id=step_id,
            state=state_snapshot,
        )

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
