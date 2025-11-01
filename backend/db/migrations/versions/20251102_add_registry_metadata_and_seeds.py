"""Add registry metadata columns and seed core tools.

Revision ID: 20251102_add_registry_metadata
Revises: 20251031_add_workflow_schema
Create Date: 2025-11-02
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from backend.models.tool_registry import CORE_TOOL_REGISTRY_SEED_DATA


revision: str = "20251102_add_registry_metadata"
down_revision: str = "20251031_add_workflow_schema"
branch_labels = None
depends_on = None


def _tools_table() -> sa.Table:
    return sa.table(
        "tools_registry",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String()),
        sa.column("module_path", sa.String()),
        sa.column("function_name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("input_schema", postgresql.JSONB),
        sa.column("output_schema", postgresql.JSONB),
        sa.column("schema_version", sa.Integer()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )


def _seed_tool_rows(bind: sa.engine.Connection) -> None:
    tools = _tools_table()
    for definition in CORE_TOOL_REGISTRY_SEED_DATA:
        exists = bind.execute(
            sa.select(tools.c.id).where(
                tools.c.module_path == definition["module_path"],
                tools.c.function_name == definition["function_name"],
            )
        ).scalar_one_or_none()
        if exists is not None:
            continue
        payload: Dict[str, Any] = {
            "id": uuid.uuid4(),
            "name": definition["name"],
            "module_path": definition["module_path"],
            "function_name": definition["function_name"],
            "description": definition.get("description"),
            "input_schema": definition.get("input_schema"),
            "output_schema": definition.get("output_schema"),
            "schema_version": definition.get("schema_version", 1),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        bind.execute(sa.insert(tools).values(**payload))



def upgrade() -> None:
    op.add_column(
        "tools_registry",
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "tools_registry",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_unique_constraint(
        "uq_tools_registry_module_path_function_name",
        "tools_registry",
        ["module_path", "function_name"],
    )

    op.add_column(
        "agents_registry",
        sa.Column(
            "access_policies",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "agents_registry",
        sa.Column(
            "quota_limits",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    bind = op.get_bind()

    bind.execute(
        sa.text(
            "UPDATE tools_registry SET schema_version = 1 WHERE schema_version IS NULL"
        )
    )
    bind.execute(
        sa.text(
            "UPDATE tools_registry SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)"
        )
    )
    bind.execute(
        sa.text(
            "UPDATE agents_registry SET access_policies = '{}'::jsonb WHERE access_policies IS NULL"
        )
    )
    bind.execute(
        sa.text(
            "UPDATE agents_registry SET quota_limits = '{}'::jsonb WHERE quota_limits IS NULL"
        )
    )

    _seed_tool_rows(bind)

    op.alter_column("tools_registry", "schema_version", server_default=None)
    op.alter_column("tools_registry", "updated_at", server_default=None)
    op.alter_column("agents_registry", "access_policies", server_default=None)
    op.alter_column("agents_registry", "quota_limits", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    tools = _tools_table()

    for definition in CORE_TOOL_REGISTRY_SEED_DATA:
        bind.execute(
            sa.delete(tools).where(
                tools.c.module_path == definition["module_path"],
                tools.c.function_name == definition["function_name"],
            )
        )

    op.drop_column("agents_registry", "quota_limits")
    op.drop_column("agents_registry", "access_policies")

    op.drop_constraint(
        "uq_tools_registry_module_path_function_name", "tools_registry", type_="unique"
    )
    op.drop_column("tools_registry", "updated_at")
    op.drop_column("tools_registry", "schema_version")
