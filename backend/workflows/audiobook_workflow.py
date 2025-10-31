"""Audiobook workflow that executes database-driven workflow revisions."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from importlib import import_module
from typing import Any, Dict, List, Optional
from uuid import UUID

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
    WorkflowManager,
    get_workflow_manager,
)

settings = get_settings()
logger = logging.getLogger(__name__)


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
        self.revision = self._load_revision(revision_id)
        self.job_context = self._build_job_context()
        self.state = self.manager.ensure_instance(
            job_id=self.job_uuid,
            revision=self.revision,
            job_context=self.job_context,
        )
        self.checkpoints = PostgresCheckpointStorage(workflow_id=job_id)

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
        agent = await self._create_agent(step.agent)
        message = self._build_message(
            "Analyze the repository at {repo_url} (git ref: {git_ref}) and respond with JSON containing summary, key components, languages,"
            " complexity, and suggested focus areas.",
            context=self.job_context,
        )
        response = await self._run_agent(agent, message, enable_checkpoint=step.checkpoint_enabled)
        parsed = self._safe_json_loads(response)
        return {"text": response, "data": parsed}

    async def _run_outline(self, step: StepDescriptor, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        agent = await self._create_agent(step.agent)
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
    ) -> tuple[str, int]:
        agent = await self._create_agent(agent_descriptor, chapter_ctx=chapter)
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
        agent = await self._create_agent(step.agent)
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
        agent = await self._create_agent(step.agent)
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
        **factory_kwargs: Any,
    ) -> Any:
        if descriptor is None:
            raise ValueError("Step is missing an agent descriptor")
        module = import_module(descriptor.module_path)
        factory = getattr(module, descriptor.factory_function)
        agent = await factory(settings, **factory_kwargs)
        return agent

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
        steps = self.state.setdefault("steps", {})
        steps[step.name] = {
            "output": payload,
            "updated_at": datetime.utcnow().isoformat(),
        }

    def _update_instance(
        self,
        step: Optional[StepDescriptor],
        *,
        status: Optional[str] = None,
        completed: bool = False,
    ) -> None:
        step_id = step.id if step else None
        self.manager.update_instance(
            job_id=self.job_uuid,
            current_step_id=step_id,
            status=status,
            state=self.state,
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
