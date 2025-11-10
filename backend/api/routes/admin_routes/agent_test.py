"""Admin routes for testing and tracing agents and workflows."""

import asyncio
import logging
import uuid
from importlib import import_module
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.api.dependencies import require_admin
from backend.config import get_settings
from backend.db.session import get_db
from backend.models.user import User
from backend.models.agent_registry import AgentRegistry
from backend.models.workflow_definition import WorkflowDefinition
from backend.models.workflow_revision import WorkflowRevision
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

    workflow_name: Optional[str] = Field(None, description="Workflow name from database (e.g., 'audiobook_workflow')")
    workflow_type: str = Field("full", description="LEGACY: Type for hardcoded workflows: full, analysis_only, outline_only")
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
    db: Optional[Session] = None,
) -> AgentTestResponse:
    """Run an agent and capture all messages and tool calls."""
    import time

    start_time = time.time()
    messages_trace: List[Dict[str, Any]] = []
    tools_trace: List[Dict[str, Any]] = []
    output_message = ""
    error = None

    try:
        # Load agent from database registry
        agent_record = None
        if db:
            agent_record = db.query(AgentRegistry).filter(AgentRegistry.name == agent_name).first()

        if agent_record:
            # Dynamically load agent from database registry
            logger.info(f"Loading agent '{agent_name}' from database registry")
            try:
                module = import_module(agent_record.module_path)
                factory_function = getattr(module, agent_record.factory_function)

                # Call factory function to create agent
                # Most agents take settings as first parameter
                agent = await factory_function(settings)
            except Exception as e:
                raise ValueError(f"Failed to load agent '{agent_name}' from registry: {str(e)}")
        else:
            # Fallback to hardcoded agents for backward compatibility
            logger.warning(f"Agent '{agent_name}' not found in database, using hardcoded fallback")
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

        # Create a thread for the agent
        thread = agent.get_new_thread()

        # Store user message
        messages_trace.append({
            "role": "user",
            "content": input_message,
            "timestamp": time.time(),
        })

        # Run agent and capture response
        # Try both streaming and direct run to capture all outputs
        response = None
        
        # First, try streaming to capture incremental updates
        async for update in agent.run_stream(input_message, thread=thread):
            # Capture streaming text updates
            if hasattr(update, "text") and update.text:
                output_message += update.text
                messages_trace.append({
                    "role": "assistant",
                    "content": update.text,
                    "timestamp": time.time(),
                    "type": "stream_chunk",
                })
            # Capture final response
            if hasattr(update, "result"):
                response = update.result
            elif hasattr(update, "message"):
                response = update.message
            elif hasattr(update, "delta") and hasattr(update.delta, "text"):
                # Handle delta updates
                delta_text = update.delta.text
                if delta_text:
                    output_message += delta_text
                    messages_trace.append({
                        "role": "assistant",
                        "content": delta_text,
                        "timestamp": time.time(),
                        "type": "delta_chunk",
                    })
        
        # If streaming didn't give us the response, run directly
        if not response:
            response = await agent.run(input_message, thread=thread)
        
        # Extract the actual response content
        # Follow the same pattern as services/outline_generator.py
        if response:
            import json
            
            # Check if response is a structured model (Pydantic)
            if hasattr(response, "model_dump"):
                output_message = json.dumps(response.model_dump(mode="json", exclude_none=True), indent=2)
            # Check if response has a "result" attribute (common pattern)
            elif hasattr(response, "result"):
                candidate = response.result
                if hasattr(candidate, "model_dump"):
                    output_message = json.dumps(candidate.model_dump(mode="json", exclude_none=True), indent=2)
                elif isinstance(candidate, dict):
                    output_message = json.dumps(candidate, indent=2)
                elif isinstance(candidate, str):
                    output_message = candidate
                else:
                    output_message = str(candidate)
            # Check if response is a dict
            elif isinstance(response, dict):
                output_message = json.dumps(response, indent=2)
            # Check if response has "text" attribute
            elif hasattr(response, "text") and response.text:
                output_message = response.text
            # Check if response is a string
            elif isinstance(response, str):
                output_message = response
            # Check if response has "contents" (ChatMessage)
            elif hasattr(response, "contents"):
                text_parts = []
                for content in response.contents:
                    if hasattr(content, "text"):
                        text_parts.append(content.text)
                    elif isinstance(content, str):
                        text_parts.append(content)
                output_message = "".join(text_parts) or str(response)
            else:
                # Fallback: convert to string
                output_message = str(response)
            
            # Add final response to trace
            if output_message:
                messages_trace.append({
                    "role": "assistant",
                    "content": output_message,
                    "timestamp": time.time(),
                    "type": "final_response",
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
    db: Session = Depends(get_db),
):
    """
    Test a single agent with tracing.

    Runs the specified agent with the given input and captures all
    messages, tool calls, and execution details.

    Agents are loaded from the database registry (agents_registry table).
    If agent is not found in registry, falls back to hardcoded agents.
    """
    try:
        result = await run_agent_with_tracing(
            agent_name=request.agent_name,
            input_message=request.input_message,
            custom_instructions=request.custom_instructions,
            chapter_data=request.chapter_data,
            db=db,
        )
        return result
    except Exception as e:
        logger.exception("Error in test_agent endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow", response_model=WorkflowTestResponse)
async def test_workflow(
    request: WorkflowTestRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Test a full or partial workflow with tracing.

    Two modes:
    1. Database workflow: Specify workflow_name to test a workflow from the database
    2. Legacy hardcoded: Use workflow_type (full, analysis_only, outline_only)

    Database workflows are loaded from workflow_definitions and workflow_revisions tables.
    """
    import time

    workflow_id = str(uuid.uuid4())
    start_time = time.time()
    stages = []
    final_result = {}
    error = None

    try:
        # Check if user requested a database workflow
        if request.workflow_name:
            # Load workflow from database
            workflow_def = db.query(WorkflowDefinition).filter(
                WorkflowDefinition.name == request.workflow_name
            ).first()

            if not workflow_def:
                raise HTTPException(
                    status_code=404,
                    detail=f"Workflow '{request.workflow_name}' not found in database"
                )

            if not workflow_def.current_revision:
                raise HTTPException(
                    status_code=400,
                    detail=f"Workflow '{request.workflow_name}' has no published revision"
                )

            # Load the current revision with steps
            from sqlalchemy.orm import selectinload
            revision = db.query(WorkflowRevision).filter(
                WorkflowRevision.id == workflow_def.current_revision_id
            ).options(selectinload(WorkflowRevision.steps)).first()

            if not revision or not revision.steps:
                raise HTTPException(
                    status_code=400,
                    detail=f"Workflow '{request.workflow_name}' revision has no steps"
                )

            logger.info(f"Testing database workflow '{request.workflow_name}' with {len(revision.steps)} steps")

            # Execute each step in order
            for step in sorted(revision.steps, key=lambda s: s.step_order):
                step_start = time.time()

                if step.agent:
                    # Load and execute agent
                    try:
                        module = import_module(step.agent.module_path)
                        factory_function = getattr(module, step.agent.factory_function)
                        agent = await factory_function(settings)

                        # Create input message based on step config
                        input_message = f"Process repository {request.repo_url} (ref: {request.git_ref})"

                        # Execute agent
                        thread = agent.get_new_thread()
                        response = await agent.run(input_message, thread=thread)

                        # Extract response content
                        output_text = ""
                        if hasattr(response, "model_dump"):
                            import json
                            output_text = json.dumps(response.model_dump(mode="json", exclude_none=True), indent=2)
                        elif isinstance(response, str):
                            output_text = response
                        else:
                            output_text = str(response)

                        stages.append({
                            "step_order": step.step_order,
                            "step_name": step.step_name,
                            "agent_name": step.agent.name,
                            "status": "completed",
                            "execution_time": time.time() - step_start,
                            "output": output_text[:500],  # Truncate for response
                        })

                        final_result[step.step_name] = output_text

                    except Exception as e:
                        logger.exception(f"Error executing step '{step.step_name}'")
                        stages.append({
                            "step_order": step.step_order,
                            "step_name": step.step_name,
                            "agent_name": step.agent.name if step.agent else None,
                            "status": "failed",
                            "error": str(e),
                        })
                        error = f"Step '{step.step_name}' failed: {str(e)}"
                        break
                elif step.plugin:
                    # Handle plugin-only step
                    try:
                        module = import_module(step.plugin.module_path)
                        plugin_function = getattr(module, step.plugin.function_name)

                        # Execute plugin (plugins are synchronous functions)
                        result = plugin_function(repo_url=request.repo_url, git_ref=request.git_ref)

                        stages.append({
                            "step_order": step.step_order,
                            "step_name": step.step_name,
                            "plugin_name": step.plugin.name,
                            "status": "completed",
                            "execution_time": time.time() - step_start,
                        })

                        final_result[step.step_name] = result

                    except Exception as e:
                        logger.exception(f"Error executing plugin step '{step.step_name}'")
                        stages.append({
                            "step_order": step.step_order,
                            "step_name": step.step_name,
                            "plugin_name": step.plugin.name if step.plugin else None,
                            "status": "failed",
                            "error": str(e),
                        })
                        error = f"Step '{step.step_name}' failed: {str(e)}"
                        break

        else:
            # LEGACY: Use hardcoded workflow types
            logger.warning(f"Using legacy hardcoded workflow type: {request.workflow_type}")
        if request.workflow_type == "analysis_only":
            # Just run analyzer
            analyzer = await analyzer_agent(settings)
            executor = AgentExecutor(analyzer)
            workflow = WorkflowBuilder().set_start_executor(executor).build()

            message = ChatMessage(
                role=Role.USER,
                contents=[
                    TextContent(
                        text=f"Analyze the repository at {request.repo_url} (ref: {request.git_ref}) and respond with JSON."
                    )
                ],
            )

            result_text = ""
            async for event in workflow.run_stream(message):
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
            # SequentialBuilder builds a workflow directly, use it without wrapping in WorkflowBuilder
            workflow = (
                SequentialBuilder()
                .participants([AgentExecutor(analyzer), AgentExecutor(outliner)])
                .build()
            )

            # Combine both instructions into a single message
            message = ChatMessage(
                role=Role.USER,
                contents=[
                    TextContent(
                        text=(
                            f"Analyze the repository at {request.repo_url} and respond with JSON. "
                            f"Then generate a {request.depth_tier} outline from the analysis and respond with JSON."
                        )
                    )
                ],
            )

            outline_text = ""
            async for event in workflow.run_stream(message):
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
            # SequentialBuilder builds a workflow directly, use it without wrapping in WorkflowBuilder
            workflow = (
                SequentialBuilder()
                .participants([AgentExecutor(analyzer), AgentExecutor(outliner)])
                .build()
            )

            # Combine both instructions into a single message
            message = ChatMessage(
                role=Role.USER,
                contents=[
                    TextContent(
                        text=(
                            f"Analyze the repository at {request.repo_url} and respond with JSON. "
                            f"Then generate a {request.depth_tier} outline from the analysis and respond with JSON."
                        )
                    )
                ],
            )

            outline_text = ""
            async for event in workflow.run_stream(message):
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


@router.get("/workflows/list")
async def list_available_workflows(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get list of available workflows from the database.

    Returns workflows from workflow_definitions table with their current revisions.
    """
    from sqlalchemy.orm import selectinload

    # Load workflows with their current revisions and steps
    workflows = db.query(WorkflowDefinition).options(
        selectinload(WorkflowDefinition.current_revision)
    ).all()

    return {
        "workflows": [
            {
                "id": str(workflow.id),
                "name": workflow.name,
                "description": workflow.description,
                "current_revision_id": str(workflow.current_revision_id) if workflow.current_revision_id else None,
                "current_version": workflow.current_revision.version if workflow.current_revision else None,
                "step_count": len(workflow.current_revision.steps) if workflow.current_revision else 0,
                "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
            }
            for workflow in workflows
        ]
    }


@router.get("/agents/list")
async def list_available_agents(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get list of available agents and their descriptions.

    Returns agents from the database registry (agents_registry table).
    Falls back to hardcoded list if no agents found in database.
    """
    # Load agents from database
    db_agents = db.query(AgentRegistry).all()

    if db_agents:
        # Return agents from database
        return {
            "agents": [
                {
                    "id": str(agent.id),
                    "name": agent.name,
                    "description": agent.description or "No description available",
                    "module_path": agent.module_path,
                    "factory_function": agent.factory_function,
                    "tools": agent.tools or [],
                    "model_identifier": agent.model_identifier,
                    "provider": agent.provider,
                    "rollout_enabled": agent.rollout_enabled,
                    "rollout_stage": agent.rollout_stage,
                }
                for agent in db_agents
            ]
        }

    # Fallback to hardcoded agents
    logger.warning("No agents found in database, returning hardcoded list")
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
