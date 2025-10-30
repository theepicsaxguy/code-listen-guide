"""Admin routes for testing and tracing agents and workflows."""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.api.dependencies import require_admin
from backend.config import get_settings
from backend.db.session import get_db
from backend.models.user import User
from backend.agents.analyzer_agent import analyzer_agent
from backend.agents.outline_agent import outline_agent
from backend.agents.script_agent import script_agent
from backend.agents.audio_agent import audio_agent
from backend.agents.postprocess_agent import postprocess_agent
from agent_framework import (
    AgentExecutor,
    ChatMessage,
    ConcurrentBuilder,
    Role,
    SequentialBuilder,
    TextContent,
    WorkflowBuilder,
)

router = APIRouter(prefix="/api/v1/admin/agent-test", tags=["admin", "agent-test"])
logger = logging.getLogger(__name__)
settings = get_settings()


class AgentTestRequest(BaseModel):
    """Request to test a single agent."""

    agent_name: str = Field(..., description="Name of agent: analyzer, outline, script, audio, postprocess")
    input_message: str = Field(..., description="Input message/prompt for the agent")
    custom_instructions: Optional[str] = Field(None, description="Override agent instructions")
    chapter_data: Optional[Dict[str, Any]] = Field(None, description="Chapter data for script agent")


class WorkflowTestRequest(BaseModel):
    """Request to test a workflow."""

    workflow_type: str = Field("full", description="Type: full, analysis_only, outline_only")
    repo_url: str = Field(..., description="Repository URL for testing")
    depth_tier: str = Field("standard", description="Depth tier: survey, standard, comprehensive")
    git_ref: str = Field("main", description="Git ref to use")
    custom_agent_instructions: Optional[Dict[str, str]] = Field(None, description="Override instructions per agent")


class AgentTestResponse(BaseModel):
    """Response from agent test."""

    agent_name: str
    input_message: str
    output_message: str
    messages: List[Dict[str, Any]]
    tools_called: List[Dict[str, Any]]
    execution_time_seconds: float
    error: Optional[str] = None


class WorkflowTestResponse(BaseModel):
    """Response from workflow test."""

    workflow_id: str
    stages: List[Dict[str, Any]]
    final_result: Dict[str, Any]
    execution_time_seconds: float
    error: Optional[str] = None


async def run_agent_with_tracing(
    agent_name: str,
    input_message: str,
    custom_instructions: Optional[str] = None,
    chapter_data: Optional[Dict[str, Any]] = None,
) -> AgentTestResponse:
    """Run an agent and capture all messages and tool calls."""
    import time

    start_time = time.time()
    messages_trace: List[Dict[str, Any]] = []
    tools_trace: List[Dict[str, Any]] = []
    output_message = ""
    error = None

    try:
        # Create the appropriate agent
        if agent_name == "analyzer":
            agent = await analyzer_agent(settings)
        elif agent_name == "outline":
            agent = await outline_agent(settings)
        elif agent_name == "script":
            agent = await script_agent(settings, chapter_data or {})
        elif agent_name == "audio":
            agent = await audio_agent(settings)
        elif agent_name == "postprocess":
            agent = await postprocess_agent(settings)
        else:
            raise ValueError(f"Unknown agent: {agent_name}")

        # Override instructions if provided
        if custom_instructions:
            # Note: This may not be directly supported by agent_framework
            # We'll need to recreate the agent with new instructions
            logger.warning("Custom instructions override may not work with current agent framework version")

        # Create a simple workflow to run the agent
        executor = AgentExecutor(agent)
        workflow = WorkflowBuilder().set_start_executor(executor).build()

        # Run with message capture
        user_message = ChatMessage(
            role=Role.USER,
            contents=[TextContent(text=input_message)],
        )

        messages_trace.append({
            "role": "user",
            "content": input_message,
            "timestamp": time.time(),
        })

        async for event in workflow.run_streaming([user_message]):
            # Capture different event types
            if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                content = event.message.text or ""
                output_message += content
                messages_trace.append({
                    "role": "assistant",
                    "content": content,
                    "timestamp": time.time(),
                })
            elif hasattr(event, "tool_call"):
                tools_trace.append({
                    "tool": getattr(event.tool_call, "name", "unknown"),
                    "arguments": getattr(event.tool_call, "arguments", {}),
                    "timestamp": time.time(),
                })

    except Exception as e:
        error = str(e)
        logger.exception(f"Error running agent {agent_name}")

    execution_time = time.time() - start_time

    return AgentTestResponse(
        agent_name=agent_name,
        input_message=input_message,
        output_message=output_message,
        messages=messages_trace,
        tools_called=tools_trace,
        execution_time_seconds=execution_time,
        error=error,
    )


@router.post("/agent", response_model=AgentTestResponse)
async def test_agent(
    request: AgentTestRequest,
    current_admin: User = Depends(require_admin),
):
    """
    Test a single agent with tracing.

    Runs the specified agent with the given input and captures all
    messages, tool calls, and execution details.
    """
    try:
        result = await run_agent_with_tracing(
            agent_name=request.agent_name,
            input_message=request.input_message,
            custom_instructions=request.custom_instructions,
            chapter_data=request.chapter_data,
        )
        return result
    except Exception as e:
        logger.exception("Error in test_agent endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow", response_model=WorkflowTestResponse)
async def test_workflow(
    request: WorkflowTestRequest,
    current_admin: User = Depends(require_admin),
):
    """
    Test a full or partial workflow with tracing.

    Supports:
    - full: Complete workflow (analysis -> outline -> ...)
    - analysis_only: Just the analysis stage
    - outline_only: Analysis + outline generation
    """
    import time

    workflow_id = str(uuid.uuid4())
    start_time = time.time()
    stages = []
    final_result = {}
    error = None

    try:
        if request.workflow_type == "analysis_only":
            # Just run analyzer
            analyzer = await analyzer_agent(settings)
            executor = AgentExecutor(analyzer)
            workflow = WorkflowBuilder().set_start_executor(executor).build()

            messages = [
                ChatMessage(
                    role=Role.USER,
                    contents=[
                        TextContent(
                            text=f"Analyze the repository at {request.repo_url} (ref: {request.git_ref}) and respond with JSON."
                        )
                    ],
                )
            ]

            result_text = ""
            async for event in workflow.run_streaming(messages):
                if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                    result_text += event.message.text or ""

            stages.append({
                "name": "analysis",
                "status": "completed",
                "output": result_text[:1000],  # Truncate for response
            })

            final_result = {"analysis": result_text}

        elif request.workflow_type == "outline_only":
            # Analysis + Outline
            analyzer = await analyzer_agent(settings)
            outliner = await outline_agent(settings)
            start_executor = (
                SequentialBuilder()
                .participants([AgentExecutor(analyzer), AgentExecutor(outliner)])
                .build()
            )
            workflow = WorkflowBuilder().set_start_executor(start_executor).build()

            messages = [
                ChatMessage(
                    role=Role.USER,
                    contents=[
                        TextContent(
                            text=f"Analyze the repository at {request.repo_url} and respond with JSON."
                        )
                    ],
                ),
                ChatMessage(
                    role=Role.USER,
                    contents=[
                        TextContent(
                            text=f"Generate a {request.depth_tier} outline from the analysis and respond with JSON."
                        )
                    ],
                ),
            ]

            outline_text = ""
            async for event in workflow.run_streaming(messages):
                if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                    outline_text += event.message.text or ""

            stages.append({
                "name": "analysis",
                "status": "completed",
            })
            stages.append({
                "name": "outline",
                "status": "completed",
                "output": outline_text[:1000],
            })

            final_result = {"outline": outline_text}

        else:
            # Full workflow (simplified version)
            # Note: Full workflow may take too long for testing
            # We'll run just the first few stages
            analyzer = await analyzer_agent(settings)
            outliner = await outline_agent(settings)
            start_executor = (
                SequentialBuilder()
                .participants([AgentExecutor(analyzer), AgentExecutor(outliner)])
                .build()
            )
            workflow = WorkflowBuilder().set_start_executor(start_executor).build()

            messages = [
                ChatMessage(
                    role=Role.USER,
                    contents=[
                        TextContent(
                            text=f"Analyze the repository at {request.repo_url} and respond with JSON."
                        )
                    ],
                ),
                ChatMessage(
                    role=Role.USER,
                    contents=[
                        TextContent(
                            text=f"Generate a {request.depth_tier} outline from the analysis and respond with JSON."
                        )
                    ],
                ),
            ]

            outline_text = ""
            async for event in workflow.run_streaming(messages):
                if hasattr(event, "message") and isinstance(event.message, ChatMessage):
                    outline_text += event.message.text or ""

            stages.append({
                "name": "analysis",
                "status": "completed",
            })
            stages.append({
                "name": "outline",
                "status": "completed",
                "output": outline_text[:1000],
            })

            final_result = {"outline": outline_text, "note": "Full workflow truncated for testing"}

    except Exception as e:
        error = str(e)
        logger.exception("Error in test_workflow endpoint")

    execution_time = time.time() - start_time

    return WorkflowTestResponse(
        workflow_id=workflow_id,
        stages=stages,
        final_result=final_result,
        execution_time_seconds=execution_time,
        error=error,
    )


@router.get("/agents/list")
async def list_available_agents(current_admin: User = Depends(require_admin)):
    """Get list of available agents and their descriptions."""
    return {
        "agents": [
            {
                "name": "analyzer",
                "description": "Repository analyzer - clones repo, parses code structure",
                "requires_input": True,
                "tools": ["clone_repository", "list_repository_files", "parse_repository"],
            },
            {
                "name": "outline",
                "description": "Outline generator - creates chapter structure from analysis",
                "requires_input": True,
                "tools": [],
            },
            {
                "name": "script",
                "description": "Script writer - generates narration scripts for chapters",
                "requires_input": True,
                "requires_chapter_data": True,
                "tools": ["save_chapter_script"],
            },
            {
                "name": "audio",
                "description": "Audio producer - synthesizes audio from scripts",
                "requires_input": True,
                "tools": [],
            },
            {
                "name": "postprocess",
                "description": "Post-processor - merges audio and creates deliverables",
                "requires_input": True,
                "tools": [],
            },
        ]
    }
