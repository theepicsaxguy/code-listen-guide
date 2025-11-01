"""Admin API for managing plugins (tools) that agents can use."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.api.dependencies import require_admin
from backend.db.session import get_db
from backend.models.tool_registry import ToolRegistry, slugify_tool_name


router = APIRouter(prefix="/api/v1/admin/plugins", tags=["admin", "plugins"])
tools_router = APIRouter(prefix="/api/v1/admin/tools", tags=["admin", "tools"])


class PluginCreate(BaseModel):
    name: str
    module_path: str
    function_name: str
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    stable_slug: Optional[str] = None
    semantic_version: str = Field(default="1.0.0")
    owning_team: str = Field(default="core-platform")
    authorization_scope: str = Field(default="internal")
    approval_mode: str = Field(default="auto")
    cost_profile: Optional[dict] = None

    @field_validator("cost_profile", mode="before")
    @classmethod
    def _validate_cost_profile(cls, value: Optional[dict]) -> Optional[dict]:
        if value is None or isinstance(value, dict):
            return value
        raise ValueError("cost_profile must be a JSON object")


class PluginUpdate(BaseModel):
    module_path: Optional[str] = None
    function_name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    stable_slug: Optional[str] = None
    semantic_version: Optional[str] = None
    owning_team: Optional[str] = None
    authorization_scope: Optional[str] = None
    approval_mode: Optional[str] = None
    cost_profile: Optional[dict] = None

    @field_validator("cost_profile", mode="before")
    @classmethod
    def _validate_cost_profile(cls, value: Optional[dict]) -> Optional[dict]:
        if value is None or isinstance(value, dict):
            return value
        raise ValueError("cost_profile must be a JSON object")


class PluginOut(BaseModel):
    id: str
    name: str
    stable_slug: str
    semantic_version: str
    module_path: str
    function_name: str
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    owning_team: str
    authorization_scope: str
    approval_mode: str
    cost_profile: dict
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class ToolRegistryItem(BaseModel):
    id: str
    name: str
    stable_slug: str
    semantic_version: str
    module_path: str
    function_name: str
    description: str
    input_schema: dict
    output_schema: dict
    owning_team: str
    authorization_scope: str
    approval_mode: str
    cost_profile: dict
    created_at: str
    updated_at: str


class ToolRegistryListResponse(BaseModel):
    tools: List[ToolRegistryItem]
    total: int
    page: int
    page_size: int


def _serialize_plugin(plugin: ToolRegistry) -> PluginOut:
    return PluginOut(
        id=str(plugin.id),
        name=plugin.name,
        stable_slug=plugin.stable_slug,
        semantic_version=plugin.semantic_version,
        module_path=plugin.module_path,
        function_name=plugin.function_name,
        description=plugin.description,
        input_schema=plugin.input_schema or {},
        output_schema=plugin.output_schema or {},
        owning_team=plugin.owning_team,
        authorization_scope=plugin.authorization_scope,
        approval_mode=plugin.approval_mode,
        cost_profile=plugin.export_cost_profile(),
        created_at=plugin.created_at.isoformat() if plugin.created_at else "",
        updated_at=plugin.updated_at.isoformat() if plugin.updated_at else "",
    )


def _serialize_registry_item(plugin: ToolRegistry) -> ToolRegistryItem:
    return ToolRegistryItem(
        id=str(plugin.id),
        name=plugin.name,
        stable_slug=plugin.stable_slug,
        semantic_version=plugin.semantic_version,
        module_path=plugin.module_path,
        function_name=plugin.function_name,
        description=plugin.description or "",
        input_schema=plugin.input_schema or {},
        output_schema=plugin.output_schema or {},
        owning_team=plugin.owning_team,
        authorization_scope=plugin.authorization_scope,
        approval_mode=plugin.approval_mode,
        cost_profile=plugin.export_cost_profile(),
        created_at=plugin.created_at.isoformat() if plugin.created_at else "",
        updated_at=plugin.updated_at.isoformat() if plugin.updated_at else "",
    )


@tools_router.get("/registry", response_model=ToolRegistryListResponse)
async def get_tool_registry(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
) -> ToolRegistryListResponse:
    query = db.query(ToolRegistry)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                ToolRegistry.name.ilike(pattern),
                ToolRegistry.stable_slug.ilike(pattern),
                ToolRegistry.description.ilike(pattern),
            )
        )
    total = query.count()
    offset = (page - 1) * page_size
    tools = (
        query.order_by(ToolRegistry.name.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    items = [_serialize_registry_item(tool) for tool in tools]
    return ToolRegistryListResponse(
        tools=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("", response_model=List[PluginOut])
async def list_plugins(
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """List all registered plugins/tools."""
    plugins = db.query(ToolRegistry).order_by(ToolRegistry.name.asc()).all()
    return [_serialize_plugin(item) for item in plugins]


@router.post("", response_model=PluginOut, status_code=status.HTTP_201_CREATED)
async def create_plugin(
    payload: PluginCreate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Create a new plugin/tool."""
    existing = db.query(ToolRegistry).filter(ToolRegistry.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Plugin with that name already exists",
        )

    stable_slug = slugify_tool_name(payload.stable_slug or payload.name)
    version = payload.semantic_version
    slug_conflict = (
        db.query(ToolRegistry)
        .filter(
            ToolRegistry.stable_slug == stable_slug,
            ToolRegistry.semantic_version == version,
        )
        .first()
    )
    if slug_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Plugin version already exists for that slug",
        )

    plugin = ToolRegistry(
        name=payload.name,
        stable_slug=stable_slug,
        semantic_version=version,
        module_path=payload.module_path,
        function_name=payload.function_name,
        description=payload.description,
        input_schema=payload.input_schema,
        output_schema=payload.output_schema,
        owning_team=payload.owning_team,
        authorization_scope=payload.authorization_scope,
        approval_mode=payload.approval_mode,
        cost_profile=ToolRegistry.normalize_cost_profile(payload.cost_profile),
    )
    db.add(plugin)
    db.commit()
    db.refresh(plugin)

    return _serialize_plugin(plugin)


@router.get("/{plugin_id}", response_model=PluginOut)
async def get_plugin(
    plugin_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Get a specific plugin."""
    plugin = db.query(ToolRegistry).filter(ToolRegistry.id == plugin_id).first()
    if not plugin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plugin not found")

    return _serialize_plugin(plugin)


@router.patch("/{plugin_id}", response_model=PluginOut)
async def update_plugin(
    plugin_id: UUID,
    payload: PluginUpdate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Update a plugin."""
    plugin = db.query(ToolRegistry).filter(ToolRegistry.id == plugin_id).first()
    if not plugin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plugin not found")

    next_slug = plugin.stable_slug
    next_version = plugin.semantic_version
    slug_version_updated = False
    if payload.stable_slug is not None:
        next_slug = slugify_tool_name(payload.stable_slug)
        slug_version_updated = True
    if payload.semantic_version is not None:
        next_version = payload.semantic_version
        slug_version_updated = True
    if slug_version_updated:
        conflict = (
            db.query(ToolRegistry)
            .filter(
                ToolRegistry.stable_slug == next_slug,
                ToolRegistry.semantic_version == next_version,
                ToolRegistry.id != plugin.id,
            )
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Plugin version already exists for that slug",
            )
        plugin.stable_slug = next_slug
        plugin.semantic_version = next_version

    if payload.module_path is not None:
        plugin.module_path = payload.module_path
    if payload.function_name is not None:
        plugin.function_name = payload.function_name
    if payload.description is not None:
        plugin.description = payload.description
    if payload.input_schema is not None:
        plugin.input_schema = payload.input_schema
    if payload.output_schema is not None:
        plugin.output_schema = payload.output_schema
    if payload.owning_team is not None:
        plugin.owning_team = payload.owning_team
    if payload.authorization_scope is not None:
        plugin.authorization_scope = payload.authorization_scope
    if payload.approval_mode is not None:
        plugin.approval_mode = payload.approval_mode
    if payload.cost_profile is not None:
        plugin.cost_profile = ToolRegistry.normalize_cost_profile(payload.cost_profile)

    db.commit()
    db.refresh(plugin)

    return _serialize_plugin(plugin)


@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plugin(
    plugin_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """Delete a plugin."""
    plugin = db.query(ToolRegistry).filter(ToolRegistry.id == plugin_id).first()
    if not plugin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plugin not found")

    db.delete(plugin)
    db.commit()

    return None


__all__ = ["router", "tools_router"]
