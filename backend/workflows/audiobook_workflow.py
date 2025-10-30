from typing import Any, Dict, List

from agent_framework import (
    AgentExecutor,
    ChatMessage,
    ConcurrentBuilder,
    Role,
    SequentialBuilder,
    TextContent,
    WorkflowBuilder,
)

from backend.agents.analyzer_agent import analyzer_agent
from backend.agents.audio_agent import audio_agent
from backend.agents.outline_agent import outline_agent
from backend.agents.postprocess_agent import postprocess_agent
from backend.agents.script_agent import script_agent
from backend.api.events import emit_job_event
from backend.config import get_settings
from backend.tools.db_tools import mark_job_status, persist_audio_parts, persist_outline
from backend.utils.checkpointing import PostgresCheckpointStorage

settings = get_settings()


class AudiobookWorkflow:
    def __init__(self, job_id: str, repo_url: str, depth_tier: str):
        self.job_id = job_id
        self.repo_url = repo_url
        self.depth_tier = depth_tier
        self.checkpoints = PostgresCheckpointStorage(workflow_id=job_id)

    async def execute(self) -> Dict[str, Any]:
        mark_job_status(self.job_id, "running", "analysis")
        analyzer = await analyzer_agent(settings)
        outliner = await outline_agent(settings)
        start_executor = (
            SequentialBuilder()
            .participants([AgentExecutor(analyzer), AgentExecutor(outliner)])
            .build()
        )
        workflow = (
            WorkflowBuilder()
            .set_start_executor(start_executor)
            .with_checkpointing(self.checkpoints)
            .build()
        )
        # Combine both instructions into a single message for the sequential workflow
        initial_message = ChatMessage(
            role=Role.USER,
            contents=[
                TextContent(
                    text=(
                        f"Analyze the repository at {self.repo_url} and respond with JSON. "
                        f"Then generate a {self.depth_tier} outline from the analysis and respond with JSON."
                    )
                )
            ],
        )
        outline_message: ChatMessage | None = None
        async for event in workflow.run_stream(initial_message):
            if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                outline_message = event.message
                emit_job_event(
                    self.job_id,
                    {"stage": "outline", "message": event.message.text or ""},
                )
        outline_text = outline_message.text if outline_message else "{}"
        persist_outline(self.job_id, outline_text)
        emit_job_event(self.job_id, {"stage": "approval_wait"})
        mark_job_status(self.job_id, "waiting_approval", "outline")
        return {"outline": outline_text}

    async def continue_after_approval(
        self, approved_outline: Dict[str, Any]
    ) -> Dict[str, Any]:
        chapters = approved_outline.get("chapters", [])
        mark_job_status(self.job_id, "running", "scripting")
        script_agents = [await script_agent(settings, chapter) for chapter in chapters]
        script_executors = [AgentExecutor(agent) for agent in script_agents]
        scripts_flow = ConcurrentBuilder().participants(script_executors).build()
        scripts_workflow = (
            WorkflowBuilder()
            .set_start_executor(scripts_flow)
            .with_checkpointing(self.checkpoints)
            .build()
        )
        scripts: List[str] = []
        # For concurrent workflow, send initial message and process all chapters
        initial_script_message = ChatMessage(
            role=Role.USER,
            contents=[
                TextContent(
                    text=f"Write narration scripts for all {len(chapters)} chapters."
                )
            ],
        )
        async for event in scripts_workflow.run_stream(initial_script_message):
            if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                scripts.append(event.message.text or "")
                emit_job_event(
                    self.job_id,
                    {
                        "stage": "scripts",
                        "completed": len(scripts),
                        "total": len(chapters),
                    },
                )
        mark_job_status(self.job_id, "running", "audio")
        audio_urls: List[str] = []
        audio_agent_instance = await audio_agent(settings)
        audio_executor = AgentExecutor(audio_agent_instance)
        batch_size = 5
        for index in range(0, len(scripts), batch_size):
            batch = scripts[index : index + batch_size]
            audio_workflow = (
                WorkflowBuilder()
                .set_start_executor(audio_executor)
                .with_checkpointing(self.checkpoints)
                .build()
            )
            # Process audio in batches - combine batch texts into single message
            batch_text = "\n\n".join(batch)
            batch_message = ChatMessage(
                role=Role.USER,
                contents=[TextContent(text=batch_text)],
            )
            async for event in audio_workflow.run_stream(batch_message):
                if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                    audio_urls.append(event.message.text or "")
                    emit_job_event(
                        self.job_id,
                        {
                            "stage": "audio",
                            "completed": len(audio_urls),
                            "total": len(scripts),
                        },
                    )
        persist_audio_parts(self.job_id, audio_urls)
        post_agent = await postprocess_agent(settings)
        post_workflow = (
            WorkflowBuilder()
            .set_start_executor(AgentExecutor(post_agent))
            .with_checkpointing(self.checkpoints)
            .build()
        )
        final_payload: str | None = None
        post_message = ChatMessage(
            role=Role.USER,
            contents=[
                TextContent(
                    text="Create the final audiobook bundle and return JSON metadata."
                )
            ],
        )
        async for event in post_workflow.run_stream(post_message):
            if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                final_payload = event.message.text or ""
                emit_job_event(self.job_id, {"stage": "postprocess"})
        mark_job_status(self.job_id, "completed", "done")
        emit_job_event(self.job_id, {"stage": "done"})
        return {"deliverables": final_payload, "chapters": len(chapters)}

    def cancel(self) -> None:
        mark_job_status(self.job_id, "cancelled", "cancelled")
        emit_job_event(self.job_id, {"stage": "cancelled"})
