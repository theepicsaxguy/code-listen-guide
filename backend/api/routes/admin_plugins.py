"""Admin API for managing plugins (tools) that agents can use."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.dependencies import require_admin
from backend.db.session import get_db
from backend.models.tool_registry import ToolRegistry
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/admin/plugins", tags=["admin", "plugins"])


class PluginCreate(BaseModel):
    name: str
    module_path: str
    function_name: str
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None


class PluginUpdate(BaseModel):
    module_path: Optional[str] = None
    function_name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None


class PluginOut(BaseModel):
    id: str
    name: str
    module_path: str
    function_name: str
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[PluginOut])
async def list_plugins(
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """List all registered plugins/tools."""
    plugins = db.query(ToolRegistry).order_by(ToolRegistry.name.asc()).all()
    return [
        PluginOut(
            id=str(p.id),
            name=p.name,
            module_path=p.module_path,
            function_name=p.function_name,
            description=p.description,
            input_schema=p.input_schema,
            output_schema=p.output_schema,
            created_at=p.created_at.isoformat() if p.created_at else "",
        )
        for p in plugins
    ]


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

    plugin = ToolRegistry(
        name=payload.name,
        module_path=payload.module_path,
        function_name=payload.function_name,
        description=payload.description,
        input_schema=payload.input_schema,
        output_schema=payload.output_schema,
    )
    db.add(plugin)
    db.commit()
    db.refresh(plugin)

    return PluginOut(
        id=str(plugin.id),
        name=plugin.name,
        module_path=plugin.module_path,
        function_name=plugin.function_name,
        description=plugin.description,
        input_schema=plugin.input_schema,
        output_schema=plugin.output_schema,
        created_at=plugin.created_at.isoformat() if plugin.created_at else "",
    )


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

    return PluginOut(
        id=str(plugin.id),
        name=plugin.name,
        module_path=plugin.module_path,
        function_name=plugin.function_name,
        description=plugin.description,
        input_schema=plugin.input_schema,
        output_schema=plugin.output_schema,
        created_at=plugin.created_at.isoformat() if plugin.created_at else "",
    )


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

    db.commit()
    db.refresh(plugin)

    return PluginOut(
        id=str(plugin.id),
        name=plugin.name,
        module_path=plugin.module_path,
        function_name=plugin.function_name,
        description=plugin.description,
        input_schema=plugin.input_schema,
        output_schema=plugin.output_schema,
        created_at=plugin.created_at.isoformat() if plugin.created_at else "",
    )


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
