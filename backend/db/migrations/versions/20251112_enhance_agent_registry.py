"""Add agent metadata columns and normalize policy/quota payloads.

Revision ID: 20251112_enhance_agent_registry
Revises: 20251102_add_registry_metadata, 20251105_add_tool_registry_validation_columns
Create Date: 2025-11-12 00:00:00.000000
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20251112_enhance_agent_registry"
down_revision = (
    "20251102_add_registry_metadata",
    "20251105_add_tool_registry_validation_columns",
)
branch_labels = None
depends_on = None


def _agents_table() -> sa.Table:
    return sa.table(
        "agents_registry",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("access_policies", postgresql.JSONB),
        sa.column("quota_limits", postgresql.JSONB),
        sa.column("memory_pointers", postgresql.JSONB),
        sa.column("rollout_enabled", sa.Boolean),
        sa.column("rollout_stage", sa.String),
    )


def _clean_string_list(values: Optional[Iterable[Any]]) -> list[str]:
    cleaned: list[str] = []
    if not values:
        return cleaned
    if isinstance(values, (str, bytes)):
        text = str(values).strip()
        return [text] if text else cleaned
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text or text in cleaned:
            continue
        cleaned.append(text)
    return cleaned


def _default_access_policies() -> dict[str, Any]:
    return {
        "default": {"allow": [], "deny": [], "metadata": {}},
        "overrides": [],
    }


def _default_quota_limits() -> dict[str, Any]:
    return {
        "default": {
            "limit": None,
            "window": None,
            "cooldown_seconds": None,
            "metadata": {},
        },
        "overrides": [],
    }


def _normalise_policy_rule(data: Mapping[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "allow": _clean_string_list(data.get("allow")),
        "deny": _clean_string_list(data.get("deny")),
        "metadata": {},
    }
    metadata = data.get("metadata")
    if isinstance(metadata, Mapping):
        payload["metadata"] = dict(metadata)
    notes = data.get("notes")
    if notes:
        payload["notes"] = str(notes)
    subject = data.get("subject")
    if subject:
        payload["subject"] = str(subject)
    return payload


def _normalise_quota_definition(data: Mapping[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "limit": None,
        "window": None,
        "cooldown_seconds": None,
        "metadata": {},
    }

    candidates: list[tuple[str, Optional[str]]] = [
        ("limit", None),
        ("max_calls", None),
        ("daily_calls", "daily"),
        ("hourly_calls", "hourly"),
        ("weekly_calls", "weekly"),
        ("monthly_calls", "monthly"),
    ]
    for key, inferred_window in candidates:
        if key in data and payload["limit"] is None:
            try:
                payload["limit"] = int(data[key]) if data[key] is not None else None
            except (TypeError, ValueError):
                payload["limit"] = None
            if inferred_window and payload["window"] is None:
                payload["window"] = inferred_window

    if isinstance(data.get("window"), str):
        window = str(data["window"]).strip()
        payload["window"] = window or payload["window"]
    if not payload["window"] and isinstance(data.get("period"), str):
        window = str(data["period"]).strip()
        payload["window"] = window or payload["window"]

    cooldown = data.get("cooldown_seconds") or data.get("cooldown")
    if cooldown is not None:
        try:
            payload["cooldown_seconds"] = int(cooldown)
        except (TypeError, ValueError):
            payload["cooldown_seconds"] = None

    metadata = data.get("metadata")
    if isinstance(metadata, Mapping):
        payload["metadata"] = dict(metadata)

    subject = data.get("subject")
    if subject:
        payload["subject"] = str(subject)

    return payload


def _normalise_access_policies(payload: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return _default_access_policies()

    if isinstance(payload.get("default"), Mapping):
        default_source: Mapping[str, Any] = payload["default"]  # type: ignore[assignment]
    else:
        default_source = payload

    overrides: list[dict[str, Any]] = []
    raw_overrides = payload.get("overrides")
    if isinstance(raw_overrides, Sequence) and not isinstance(raw_overrides, (str, bytes)):
        for item in raw_overrides:
            if isinstance(item, Mapping):
                overrides.append(_normalise_policy_rule(item))

    return {
        "default": _normalise_policy_rule(default_source),
        "overrides": overrides,
    }


def _normalise_quota_limits(payload: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return _default_quota_limits()

    if isinstance(payload.get("default"), Mapping):
        default_source: Mapping[str, Any] = payload["default"]  # type: ignore[assignment]
    else:
        default_source = payload

    overrides: list[dict[str, Any]] = []
    raw_overrides = payload.get("overrides")
    if isinstance(raw_overrides, Sequence) and not isinstance(raw_overrides, (str, bytes)):
        for item in raw_overrides:
            if isinstance(item, Mapping):
                overrides.append(_normalise_quota_definition(item))

    return {
        "default": _normalise_quota_definition(default_source),
        "overrides": overrides,
    }


def upgrade() -> None:
    op.add_column(
        "agents_registry",
        sa.Column("model_identifier", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "agents_registry",
        sa.Column("provider", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "agents_registry",
        sa.Column("system_prompt", sa.Text(), nullable=True),
    )
    op.add_column(
        "agents_registry",
        sa.Column(
            "memory_pointers",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "agents_registry",
        sa.Column(
            "rollout_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "agents_registry",
        sa.Column("rollout_stage", sa.String(length=100), nullable=True),
    )

    op.alter_column(
        "agents_registry",
        "access_policies",
        server_default=sa.text(
            "'{""default"": {""allow"": [], ""deny"": [], ""metadata"": {}}, ""overrides"": []}'::jsonb"
        ),
        existing_type=postgresql.JSONB,
    )
    op.alter_column(
        "agents_registry",
        "quota_limits",
        server_default=sa.text(
            "'{""default"": {""limit"": null, ""window"": null, ""cooldown_seconds"": null, ""metadata"": {}}, ""overrides"": []}'::jsonb"
        ),
        existing_type=postgresql.JSONB,
    )

    bind = op.get_bind()
    agents = _agents_table()
    rows = bind.execute(
        sa.select(agents.c.id, agents.c.access_policies, agents.c.quota_limits)
    ).fetchall()

    for row in rows:
        policies = _normalise_access_policies(row.access_policies)
        quotas = _normalise_quota_limits(row.quota_limits)
        bind.execute(
            sa.update(agents)
            .where(agents.c.id == row.id)
            .values(
                access_policies=policies,
                quota_limits=quotas,
            )
        )

    op.alter_column(
        "agents_registry",
        "access_policies",
        server_default=None,
        existing_type=postgresql.JSONB,
    )
    op.alter_column(
        "agents_registry",
        "quota_limits",
        server_default=None,
        existing_type=postgresql.JSONB,
    )
    op.alter_column(
        "agents_registry",
        "memory_pointers",
        server_default=None,
        existing_type=postgresql.JSONB,
    )
    op.alter_column(
        "agents_registry",
        "rollout_enabled",
        server_default=None,
        existing_type=sa.Boolean(),
    )


def downgrade() -> None:
    bind = op.get_bind()
    agents = _agents_table()
    rows = bind.execute(
        sa.select(agents.c.id, agents.c.access_policies, agents.c.quota_limits)
    ).fetchall()

    for row in rows:
        default_policy = {}
        if isinstance(row.access_policies, Mapping):
            default_section = row.access_policies.get("default", {})  # type: ignore[assignment]
            if isinstance(default_section, Mapping):
                default_policy = {
                    "allow": _clean_string_list(default_section.get("allow")),
                    "deny": _clean_string_list(default_section.get("deny")),
                }
        bind.execute(
            sa.update(agents)
            .where(agents.c.id == row.id)
            .values(
                access_policies=default_policy,
                quota_limits={},
            )
        )

    op.drop_column("agents_registry", "rollout_stage")
    op.drop_column("agents_registry", "rollout_enabled")
    op.drop_column("agents_registry", "memory_pointers")
    op.drop_column("agents_registry", "system_prompt")
    op.drop_column("agents_registry", "provider")
    op.drop_column("agents_registry", "model_identifier")
