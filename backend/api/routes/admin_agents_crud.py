"""Admin API for CRUD operations on agents."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from backend.api.dependencies import require_admin
from backend.db.session import get_db
from backend.models.agent_registry import AgentRegistry
from backend.models.tool_registry import ToolRegistry


router = APIRouter(prefix="/api/v1/admin/agents", tags=["admin", "agents"])


class PolicyRulePayload(BaseModel):
    subject: Optional[str] = None
    allow: List[str] = Field(default_factory=list)
    deny: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class AgentPolicyPayload(BaseModel):
    default: PolicyRulePayload = Field(default_factory=PolicyRulePayload)
    overrides: List[PolicyRulePayload] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class QuotaDefinitionPayload(BaseModel):
    subject: Optional[str] = None
    limit: Optional[int] = Field(default=None, ge=0)
    window: Optional[str] = Field(default=None, min_length=1)
    cooldown_seconds: Optional[int] = Field(default=None, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class AgentQuotaPayload(BaseModel):
    default: QuotaDefinitionPayload = Field(default_factory=QuotaDefinitionPayload)
    overrides: List[QuotaDefinitionPayload] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class AgentCreate(BaseModel):
    name: str
    module_path: str
    factory_function: str
    description: Optional[str] = None
    config_schema: Optional[dict] = None
    tools: Optional[List[str]] = None
    model_identifier: Optional[str] = None
    provider: Optional[str] = None
    system_prompt: Optional[str] = None
    memory_pointers: Optional[List[str]] = None
    rollout_enabled: bool = False
    rollout_stage: Optional[str] = None
    access_policies: Optional[AgentPolicyPayload] = None
    quota_limits: Optional[AgentQuotaPayload] = None

    @field_validator("memory_pointers", mode="after")
    @classmethod
    def _clean_memory(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        cleaned: List[str] = []
        for pointer in value:
            if pointer is None:
                continue
            text = str(pointer).strip()
            if not text or text in cleaned:
                continue
            cleaned.append(text)
        return cleaned

    @field_validator("system_prompt", mode="before")
    @classmethod
    def _strip_prompt(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = str(value)
        return text.strip() or None

    @field_validator("model_identifier", "provider", "rollout_stage", mode="before")
    @classmethod
    def _strip_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = str(value)
        return text.strip() or None


class AgentUpdate(BaseModel):
    module_path: Optional[str] = None
    factory_function: Optional[str] = None
    description: Optional[str] = None
    config_schema: Optional[dict] = None
    tools: Optional[List[str]] = None
    model_identifier: Optional[str] = None
    provider: Optional[str] = None
    system_prompt: Optional[str] = None
    memory_pointers: Optional[List[str]] = None
    rollout_enabled: Optional[bool] = None
    rollout_stage: Optional[str] = None
    access_policies: Optional[AgentPolicyPayload] = None
    quota_limits: Optional[AgentQuotaPayload] = None

    @field_validator("memory_pointers", mode="after")
    @classmethod
    def _clean_memory(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        cleaned: List[str] = []
        for pointer in value:
            if pointer is None:
                continue
            text = str(pointer).strip()
            if not text or text in cleaned:
                continue
            cleaned.append(text)
        return cleaned

    @field_validator("system_prompt", mode="before")
    @classmethod
    def _strip_prompt(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = str(value)
        return text.strip() or None

    @field_validator("model_identifier", "provider", "rollout_stage", mode="before")
    @classmethod
    def _strip_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = str(value)
        return text.strip() or None


class AgentOut(BaseModel):
    id: str
    name: str
    module_path: str
    factory_function: str
    description: Optional[str] = None
    config_schema: Optional[dict] = None
    tools: Optional[List[dict]] = None
    model_identifier: Optional[str] = None
    provider: Optional[str] = None
    system_prompt: Optional[str] = None
    memory_pointers: List[str]
    rollout_enabled: bool
    rollout_stage: Optional[str] = None
    access_policies: Dict[str, Any]
    quota_limits: Dict[str, Any]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class AgentRegistryItem(BaseModel):
    id: str
    name: str
    module_path: str
    factory_function: str
    description: str
    config_schema: dict
    tools: List[str]
    model_identifier: Optional[str]
    provider: Optional[str]
    system_prompt: Optional[str]
    memory_pointers: List[str]
    rollout_enabled: bool
    rollout_stage: Optional[str]
    access_policies: Dict[str, Any]
    quota_limits: Dict[str, Any]
    created_at: str
    updated_at: str


class AgentRegistryListResponse(BaseModel):
    agents: List[AgentRegistryItem]
    total: int
    page: int
    page_size: int


def _serialize_agent(agent: AgentRegistry, tools: Optional[List[dict]]) -> AgentOut:
    return AgentOut(
        id=str(agent.id),
        name=agent.name,
        module_path=agent.module_path,
        factory_function=agent.factory_function,
        description=agent.description,
        config_schema=agent.config_schema or {},
        tools=tools,
        model_identifier=agent.model_identifier,
        provider=agent.provider,
        system_prompt=agent.system_prompt,
        memory_pointers=AgentRegistry.normalize_memory_pointers(agent.memory_pointers),
        rollout_enabled=bool(agent.rollout_enabled),
        rollout_stage=agent.rollout_stage,
        access_policies=AgentRegistry.normalize_access_policies(agent.access_policies),
        quota_limits=AgentRegistry.normalize_quota_limits(agent.quota_limits),
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        updated_at=agent.updated_at.isoformat() if agent.updated_at else "",
    )


def _serialize_registry_item(agent: AgentRegistry) -> AgentRegistryItem:
    tool_refs: List[str] = []
    if isinstance(agent.tools, list):
        tool_refs = [str(item) for item in agent.tools]
    return AgentRegistryItem(
        id=str(agent.id),
        name=agent.name,
        module_path=agent.module_path,
        factory_function=agent.factory_function,
        description=agent.description or "",
        config_schema=agent.config_schema or {},
        tools=tool_refs,
        model_identifier=agent.model_identifier,
        provider=agent.provider,
        system_prompt=agent.system_prompt,
        memory_pointers=AgentRegistry.normalize_memory_pointers(agent.memory_pointers),
        rollout_enabled=bool(agent.rollout_enabled),
        rollout_stage=agent.rollout_stage,
        access_policies=AgentRegistry.normalize_access_policies(agent.access_policies),
        quota_limits=AgentRegistry.normalize_quota_limits(agent.quota_limits),
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        updated_at=agent.updated_at.isoformat() if agent.updated_at else "",
    )


def _resolve_tools(db: Session, tool_refs: Optional[List[str]]) -> Optional[List[dict]]:
    """Resolve tool references (names or IDs) to full tool objects."""
    if not tool_refs:
        return None

    tools = []
    for ref in tool_refs:
        tool = None
        try:
            tool = db.query(ToolRegistry).filter(ToolRegistry.id == UUID(ref)).first()
        except (ValueError, AttributeError):
            pass
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


@router.get("/registry", operation_id="getAgentRegistry", response_model=AgentRegistryListResponse)
async def get_agent_registry(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
) -> AgentRegistryListResponse:
    query = db.query(AgentRegistry)
    if search:
        pattern = f"%{search}%"
        query = query.filter(AgentRegistry.name.ilike(pattern))
    total = query.count()
    offset = (page - 1) * page_size
    agents = (
        query.order_by(AgentRegistry.name.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    items = [_serialize_registry_item(agent) for agent in agents]
    return AgentRegistryListResponse(
        agents=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/list", operation_id="listAgents", response_model=List[AgentOut])
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
            tool_refs = agent.tools if isinstance(agent.tools, list) else []
            tools = _resolve_tools(db, tool_refs)
        result.append(_serialize_agent(agent, tools))
    return result


@router.post("", operation_id="createAgent", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
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

    tools_data = None
    if payload.tools:
        tools_data = []
        for tool_ref in payload.tools:
            resolved = _resolve_tools(db, [tool_ref])
            if not resolved:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tool '{tool_ref}' not found",
                )
            tools_data.append(tool_ref)

    agent = AgentRegistry(
        name=payload.name,
        module_path=payload.module_path,
        factory_function=payload.factory_function,
        description=payload.description,
        config_schema=payload.config_schema,
        tools=tools_data,
        model_identifier=payload.model_identifier,
        provider=payload.provider,
        system_prompt=payload.system_prompt,
        memory_pointers=AgentRegistry.normalize_memory_pointers(payload.memory_pointers),
        rollout_enabled=bool(payload.rollout_enabled),
        rollout_stage=payload.rollout_stage,
        access_policies=AgentRegistry.normalize_access_policies(
            payload.access_policies.model_dump() if payload.access_policies else None
        ),
        quota_limits=AgentRegistry.normalize_quota_limits(
            payload.quota_limits.model_dump() if payload.quota_limits else None
        ),
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    resolved_tools = _resolve_tools(db, tools_data) if tools_data else None

    return _serialize_agent(agent, resolved_tools)


@router.get("/{agent_id}", operation_id="getAgent", response_model=AgentOut)
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

    return _serialize_agent(agent, tools)


@router.patch("/{agent_id}", operation_id="updateAgent", response_model=AgentOut)
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
        tools_data: List[str] = []
        for tool_ref in payload.tools:
            resolved = _resolve_tools(db, [tool_ref])
            if not resolved:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tool '{tool_ref}' not found",
                )
            tools_data.append(tool_ref)
        agent.tools = tools_data
    if payload.model_identifier is not None:
        agent.model_identifier = payload.model_identifier
    if payload.provider is not None:
        agent.provider = payload.provider
    if payload.system_prompt is not None:
        agent.system_prompt = payload.system_prompt
    if payload.memory_pointers is not None:
        agent.memory_pointers = AgentRegistry.normalize_memory_pointers(payload.memory_pointers)
    if payload.rollout_enabled is not None:
        agent.rollout_enabled = bool(payload.rollout_enabled)
    if payload.rollout_stage is not None:
        agent.rollout_stage = payload.rollout_stage
    if payload.access_policies is not None:
        agent.access_policies = AgentRegistry.normalize_access_policies(
            payload.access_policies.model_dump()
        )
    if payload.quota_limits is not None:
        agent.quota_limits = AgentRegistry.normalize_quota_limits(
            payload.quota_limits.model_dump()
        )

    db.commit()
    db.refresh(agent)

    tools = None
    if agent.tools:
        tool_refs = agent.tools if isinstance(agent.tools, list) else []
        tools = _resolve_tools(db, tool_refs)

    return _serialize_agent(agent, tools)


@router.delete("/{agent_id}", operation_id="deleteAgent", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Delete an agent."""
    agent = db.query(AgentRegistry).filter(AgentRegistry.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

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
