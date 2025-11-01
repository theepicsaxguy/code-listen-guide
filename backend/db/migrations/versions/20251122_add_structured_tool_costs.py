"""Add structured cost fields to tool registry.

Revision ID: 20251122_add_structured_tool_costs
Revises: 20251118_extend_tool_registry_metadata
Create Date: 2025-11-22 00:00:00.000000
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Tuple

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20251122_add_structured_tool_costs"
down_revision = "20251118_extend_tool_registry_metadata"
branch_labels = None
depends_on = None


TOOLS_TABLE = sa.table(
    "tools_registry",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("cost_profile", postgresql.JSONB),
    sa.column("cost_per_call_cents", sa.Integer()),
    sa.column("cost_per_1k_tokens_cents", sa.Integer()),
    sa.column("cost_per_second_cents", sa.Integer()),
    sa.column("cost_currency", sa.String()),
    sa.column("cost_provider", sa.String()),
)


def _coerce_cost_value(raw: Any) -> Optional[int]:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return int(round(raw))
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        try:
            numeric = float(text)
        except ValueError:
            return None
        return int(round(numeric))
    return None


def _extract_cost_fields(payload: Mapping[str, Any]) -> Dict[str, Optional[Any]]:
    def _lookup(keys: Tuple[str, ...]) -> Optional[Any]:
        for candidate in keys:
            if candidate in payload and payload[candidate] is not None:
                return payload[candidate]
        return None

    billing_block = payload.get("billing")
    billing_mapping: Mapping[str, Any] = billing_block if isinstance(billing_block, Mapping) else {}

    per_call = _coerce_cost_value(
        _lookup(("cost_per_call_cents", "costPerCallCents", "x-cost-per-call-cents"))
        or _coerce_cost_value(billing_mapping.get("cost_per_call_cents"))
    )
    per_tokens = _coerce_cost_value(
        _lookup(
            (
                "cost_per_1k_tokens_cents",
                "costPer1kTokensCents",
                "x-cost-per-1k-tokens-cents",
            )
        )
        or _coerce_cost_value(billing_mapping.get("cost_per_1k_tokens_cents"))
    )
    per_second = _coerce_cost_value(
        _lookup(("cost_per_second_cents", "costPerSecondCents", "x-cost-per-second-cents"))
        or _coerce_cost_value(billing_mapping.get("cost_per_second_cents"))
    )

    currency_candidate = _lookup(("currency", "cost_currency", "billing_currency"))
    if currency_candidate is None and isinstance(billing_mapping.get("currency"), str):
        currency_candidate = billing_mapping.get("currency")
    currency_value = currency_candidate.strip() if isinstance(currency_candidate, str) else None

    provider_candidate = _lookup(("provider", "vendor", "billing_provider"))
    if provider_candidate is None and isinstance(billing_mapping.get("provider"), str):
        provider_candidate = billing_mapping.get("provider")
    provider_value = provider_candidate.strip() if isinstance(provider_candidate, str) else None

    return {
        "cost_per_call_cents": per_call,
        "cost_per_1k_tokens_cents": per_tokens,
        "cost_per_second_cents": per_second,
        "currency": currency_value or None,
        "provider": provider_value or None,
    }


def _normalize_cost_profile(raw: Any) -> Tuple[Dict[str, Any], Dict[str, Optional[Any]]]:
    if not isinstance(raw, Mapping):
        return {}, {
            "cost_per_call_cents": None,
            "cost_per_1k_tokens_cents": None,
            "cost_per_second_cents": None,
            "currency": None,
            "provider": None,
        }
    normalized: Dict[str, Any] = {}
    for key, value in raw.items():
        if isinstance(value, Mapping):
            normalized[key] = dict(value)
        else:
            normalized[key] = value
    extracted = _extract_cost_fields(normalized)
    for field, payload_value in extracted.items():
        if payload_value is not None:
            normalized[field] = payload_value
    return normalized, extracted


def _backfill_cost_fields(bind: sa.engine.Connection) -> None:
    rows = bind.execute(
        sa.select(
            TOOLS_TABLE.c.id,
            TOOLS_TABLE.c.cost_profile,
        )
    ).fetchall()
    for row in rows:
        mapping = row._mapping
        tool_id = mapping["id"]
        normalized, extracted = _normalize_cost_profile(mapping["cost_profile"] or {})
        has_pricing = any(
            extracted[key] is not None
            for key in ("cost_per_call_cents", "cost_per_1k_tokens_cents", "cost_per_second_cents")
        )
        bind.execute(
            TOOLS_TABLE.update()
            .where(TOOLS_TABLE.c.id == tool_id)
            .values(
                cost_profile=normalized,
                cost_per_call_cents=extracted["cost_per_call_cents"],
                cost_per_1k_tokens_cents=extracted["cost_per_1k_tokens_cents"],
                cost_per_second_cents=extracted["cost_per_second_cents"],
                cost_currency=extracted["currency"] or ("USD" if has_pricing else None),
                cost_provider=extracted["provider"],
            )
        )


def upgrade() -> None:
    op.add_column("tools_registry", sa.Column("cost_per_call_cents", sa.Integer(), nullable=True))
    op.add_column("tools_registry", sa.Column("cost_per_1k_tokens_cents", sa.Integer(), nullable=True))
    op.add_column("tools_registry", sa.Column("cost_per_second_cents", sa.Integer(), nullable=True))
    op.add_column("tools_registry", sa.Column("cost_currency", sa.String(length=16), nullable=True))
    op.add_column("tools_registry", sa.Column("cost_provider", sa.String(length=255), nullable=True))

    bind = op.get_bind()
    _backfill_cost_fields(bind)


def downgrade() -> None:
    op.drop_column("tools_registry", "cost_provider")
    op.drop_column("tools_registry", "cost_currency")
    op.drop_column("tools_registry", "cost_per_second_cents")
    op.drop_column("tools_registry", "cost_per_1k_tokens_cents")
    op.drop_column("tools_registry", "cost_per_call_cents")
