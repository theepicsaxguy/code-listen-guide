"""Admin API for CRUD operations on agents."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.dependencies import require_admin
from backend.db.session import get_db
from backend.models.agent_registry import AgentRegistry
from backend.models.tool_registry import ToolRegistry
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/admin/agents", tags=["admin", "agents"])


class AgentCreate(BaseModel):
    name: str
    module_path: str
    factory_function: str
    description: Optional[str] = None
    config_schema: Optional[dict] = None
    tools: Optional[List[str]] = None  # List of tool/plugin names or IDs


class AgentUpdate(BaseModel):
    module_path: Optional[str] = None
    factory_function: Optional[str] = None
    description: Optional[str] = None
    config_schema: Optional[dict] = None
    tools: Optional[List[str]] = None  # List of tool/plugin names or IDs


class AgentOut(BaseModel):
    id: str
    name: str
    module_path: str
    factory_function: str
    description: Optional[str] = None
    config_schema: Optional[dict] = None
    tools: Optional[List[dict]] = None  # Full tool details
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


def _resolve_tools(db: Session, tool_refs: Optional[List[str]]) -> Optional[List[dict]]:
    """Resolve tool references (names or IDs) to full tool objects."""
    if not tool_refs:
        return None

    tools = []
    for ref in tool_refs:
        tool = None
        # Try by ID first if it looks like a UUID
        try:
            tool = db.query(ToolRegistry).filter(ToolRegistry.id == UUID(ref)).first()
        except (ValueError, AttributeError):
            pass
        # If not found, try by name
        if not tool:
            tool = db.query(ToolRegistry).filter(ToolRegistry.name == ref).first()

        if tool:
            tools.append({
                "id": str(tool.id),
                "name": tool.name,
                "module_path": tool.module_path,
                "function_name": tool.function_name,
                "description": tool.description,
            })

    return tools if tools else None


@router.get("/list", response_model=List[AgentOut])
async def list_agents(
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """List all registered agents."""
    agents = db.query(AgentRegistry).order_by(AgentRegistry.name.asc()).all()
    result = []
    for agent in agents:
        tools = None
        if agent.tools:
            # agent.tools is stored as JSON, could be list of tool IDs/names
            tool_refs = agent.tools if isinstance(agent.tools, list) else []
            tools = _resolve_tools(db, tool_refs)

        result.append(
            AgentOut(
                id=str(agent.id),
                name=agent.name,
                module_path=agent.module_path,
                factory_function=agent.factory_function,
                description=agent.description,
                config_schema=agent.config_schema,
                tools=tools,
                created_at=agent.created_at.isoformat() if agent.created_at else "",
                updated_at=agent.updated_at.isoformat() if agent.updated_at else "",
            )
        )
    return result


@router.post("", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Create a new agent."""
    existing = db.query(AgentRegistry).filter(AgentRegistry.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Agent with that name already exists",
        )

    # Validate tool references if provided
    tools_data = None
    if payload.tools:
        tools_data = []
        for tool_ref in payload.tools:
            tool = None
            # Try by ID first if it looks like a UUID
            try:
                tool = db.query(ToolRegistry).filter(ToolRegistry.id == UUID(tool_ref)).first()
            except (ValueError, AttributeError):
                pass
            # If not found, try by name
            if not tool:
                tool = db.query(ToolRegistry).filter(ToolRegistry.name == tool_ref).first()
            if not tool:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tool '{tool_ref}' not found",
                )
            tools_data.append(tool_ref)  # Store as list of IDs/names

    agent = AgentRegistry(
        name=payload.name,
        module_path=payload.module_path,
        factory_function=payload.factory_function,
        description=payload.description,
        config_schema=payload.config_schema,
        tools=tools_data,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    resolved_tools = _resolve_tools(db, tools_data) if tools_data else None

    return AgentOut(
        id=str(agent.id),
        name=agent.name,
        module_path=agent.module_path,
        factory_function=agent.factory_function,
        description=agent.description,
        config_schema=agent.config_schema,
        tools=resolved_tools,
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        updated_at=agent.updated_at.isoformat() if agent.updated_at else "",
    )


@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Get a specific agent."""
    agent = db.query(AgentRegistry).filter(AgentRegistry.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    tools = None
    if agent.tools:
        tool_refs = agent.tools if isinstance(agent.tools, list) else []
        tools = _resolve_tools(db, tool_refs)

    return AgentOut(
        id=str(agent.id),
        name=agent.name,
        module_path=agent.module_path,
        factory_function=agent.factory_function,
        description=agent.description,
        config_schema=agent.config_schema,
        tools=tools,
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        updated_at=agent.updated_at.isoformat() if agent.updated_at else "",
    )


@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: UUID,
    payload: AgentUpdate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Update an agent."""
    agent = db.query(AgentRegistry).filter(AgentRegistry.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    if payload.module_path is not None:
        agent.module_path = payload.module_path
    if payload.factory_function is not None:
        agent.factory_function = payload.factory_function
    if payload.description is not None:
        agent.description = payload.description
    if payload.config_schema is not None:
        agent.config_schema = payload.config_schema
    if payload.tools is not None:
        # Validate tool references
        tools_data = []
        for tool_ref in payload.tools:
            tool = None
            # Try by ID first if it looks like a UUID
            try:
                tool = db.query(ToolRegistry).filter(ToolRegistry.id == UUID(tool_ref)).first()
            except (ValueError, AttributeError):
                pass
            # If not found, try by name
            if not tool:
                tool = db.query(ToolRegistry).filter(ToolRegistry.name == tool_ref).first()
            if not tool:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tool '{tool_ref}' not found",
                )
            tools_data.append(tool_ref)
        agent.tools = tools_data

    db.commit()
    db.refresh(agent)

    tools = None
    if agent.tools:
        tool_refs = agent.tools if isinstance(agent.tools, list) else []
        tools = _resolve_tools(db, tool_refs)

    return AgentOut(
        id=str(agent.id),
        name=agent.name,
        module_path=agent.module_path,
        factory_function=agent.factory_function,
        description=agent.description,
        config_schema=agent.config_schema,
        tools=tools,
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        updated_at=agent.updated_at.isoformat() if agent.updated_at else "",
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Delete an agent."""
    agent = db.query(AgentRegistry).filter(AgentRegistry.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    # Check if agent is used in any workflow steps
    from backend.models.workflow_step import WorkflowStep
    steps_using_agent = db.query(WorkflowStep).filter(WorkflowStep.agent_id == agent_id).count()
    if steps_using_agent > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete agent: it is used in {steps_using_agent} workflow step(s)",
        )

    db.delete(agent)
    db.commit()

    return None
