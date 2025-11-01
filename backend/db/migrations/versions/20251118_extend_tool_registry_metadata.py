"""Extend tool registry with slug, version, and governance metadata.

Revision ID: 20251118_extend_tool_registry_metadata
Revises: 20251112_enhance_agent_registry
Create Date: 2025-11-18 00:00:00.000000
"""

from __future__ import annotations

import re
from typing import Any, Dict

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20251118_extend_tool_registry_metadata"
down_revision = "20251112_enhance_agent_registry"
branch_labels = None
depends_on = None


TOOLS_TABLE = sa.table(
    "tools_registry",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("name", sa.String()),
    sa.column("stable_slug", sa.String()),
    sa.column("semantic_version", sa.String()),
    sa.column("owning_team", sa.String()),
    sa.column("authorization_scope", sa.String()),
    sa.column("approval_mode", sa.String()),
    sa.column("cost_profile", postgresql.JSONB),
)


def _slugify(value: str) -> str:
    collapsed = re.sub(r"[^a-z0-9]+", "-", value.lower())
    trimmed = collapsed.strip("-")
    return trimmed or "tool"


def _default_cost_profile() -> Dict[str, Any]:
    return {"unit": "call", "estimated_cost_usd": 0.0}


def _backfill_tool_metadata(bind: sa.engine.Connection) -> None:
    rows = bind.execute(
        sa.select(
            TOOLS_TABLE.c.id,
            TOOLS_TABLE.c.name,
            TOOLS_TABLE.c.stable_slug,
            TOOLS_TABLE.c.semantic_version,
            TOOLS_TABLE.c.owning_team,
            TOOLS_TABLE.c.authorization_scope,
            TOOLS_TABLE.c.approval_mode,
            TOOLS_TABLE.c.cost_profile,
        )
    ).fetchall()
    for row in rows:
        record = row._mapping
        tool_id = record["id"]
        name = record["name"] or "tool"
        slug = record["stable_slug"] or _slugify(name)
        semantic_version = record["semantic_version"] or "1.0.0"
        owning_team = record["owning_team"] or "core-platform"
        authorization_scope = record["authorization_scope"] or "internal"
        approval_mode = record["approval_mode"] or "auto"
        cost_profile = record["cost_profile"] or _default_cost_profile()
        bind.execute(
            TOOLS_TABLE.update()
            .where(TOOLS_TABLE.c.id == tool_id)
            .values(
                stable_slug=slug,
                semantic_version=semantic_version,
                owning_team=owning_team,
                authorization_scope=authorization_scope,
                approval_mode=approval_mode,
                cost_profile=cost_profile,
            )
        )


def upgrade() -> None:
    op.add_column("tools_registry", sa.Column("stable_slug", sa.String(length=255), nullable=True))
    op.add_column(
        "tools_registry",
        sa.Column("semantic_version", sa.String(length=32), nullable=False, server_default="1.0.0"),
    )
    op.add_column(
        "tools_registry",
        sa.Column("owning_team", sa.String(length=255), nullable=False, server_default="core-platform"),
    )
    op.add_column(
        "tools_registry",
        sa.Column("authorization_scope", sa.String(length=255), nullable=False, server_default="internal"),
    )
    op.add_column(
        "tools_registry",
        sa.Column("approval_mode", sa.String(length=64), nullable=False, server_default="auto"),
    )
    op.add_column(
        "tools_registry",
        sa.Column(
            "cost_profile",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    bind = op.get_bind()
    _backfill_tool_metadata(bind)

    op.alter_column("tools_registry", "stable_slug", nullable=False)
    op.create_unique_constraint(
        "uq_tools_registry_slug_version",
        "tools_registry",
        ["stable_slug", "semantic_version"],
    )

    op.alter_column("tools_registry", "semantic_version", server_default=None)
    op.alter_column("tools_registry", "owning_team", server_default=None)
    op.alter_column("tools_registry", "authorization_scope", server_default=None)
    op.alter_column("tools_registry", "approval_mode", server_default=None)
    op.alter_column("tools_registry", "cost_profile", server_default=None)


def downgrade() -> None:
    op.drop_constraint("uq_tools_registry_slug_version", "tools_registry", type_="unique")
    op.drop_column("tools_registry", "cost_profile")
    op.drop_column("tools_registry", "approval_mode")
    op.drop_column("tools_registry", "authorization_scope")
    op.drop_column("tools_registry", "owning_team")
    op.drop_column("tools_registry", "semantic_version")
    op.drop_column("tools_registry", "stable_slug")
