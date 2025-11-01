"""SQLAlchemy model describing registered agents available to workflows."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from sqlalchemy import Boolean, Column, DateTime, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.db.base import Base


def _clean_string_list(values: Optional[Iterable[Any]]) -> List[str]:
    cleaned: List[str] = []
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


def default_access_policies() -> Dict[str, Any]:
    return {
        "default": {"allow": [], "deny": [], "metadata": {}},
        "overrides": [],
    }


def default_quota_limits() -> Dict[str, Any]:
    return {
        "default": {
            "limit": None,
            "window": None,
            "cooldown_seconds": None,
            "metadata": {},
        },
        "overrides": [],
    }


def default_memory_pointers() -> List[str]:
    return []


def _normalise_policy_rule(data: Mapping[str, Any]) -> Dict[str, Any]:
    allow = _clean_string_list(data.get("allow"))
    deny = _clean_string_list(data.get("deny"))
    payload: Dict[str, Any] = {
        "allow": allow,
        "deny": deny,
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


def _normalise_quota_definition(data: Mapping[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "limit": None,
        "window": None,
        "cooldown_seconds": None,
        "metadata": {},
    }

    candidates: List[tuple[str, Optional[str]]] = [
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

    if data.get("window") and isinstance(data.get("window"), str):
        payload["window"] = str(data["window"]).strip() or None
    if data.get("period") and not payload["window"]:
        payload["window"] = str(data["period"]).strip() or None

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


def normalise_access_policies(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        return default_access_policies()

    default_source: Mapping[str, Any]
    if isinstance(payload.get("default"), Mapping):
        default_source = payload.get("default", {})  # type: ignore[assignment]
    else:
        default_source = payload

    overrides: List[Dict[str, Any]] = []
    raw_overrides = payload.get("overrides")
    if isinstance(raw_overrides, Sequence) and not isinstance(raw_overrides, (str, bytes)):
        for item in raw_overrides:
            if isinstance(item, Mapping):
                overrides.append(_normalise_policy_rule(item))

    result = {
        "default": _normalise_policy_rule(default_source),
        "overrides": overrides,
    }
    return result


def normalise_quota_limits(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        return default_quota_limits()

    default_source: Mapping[str, Any]
    if isinstance(payload.get("default"), Mapping):
        default_source = payload.get("default", {})  # type: ignore[assignment]
    else:
        default_source = payload

    overrides: List[Dict[str, Any]] = []
    raw_overrides = payload.get("overrides")
    if isinstance(raw_overrides, Sequence) and not isinstance(raw_overrides, (str, bytes)):
        for item in raw_overrides:
            if isinstance(item, Mapping):
                overrides.append(_normalise_quota_definition(item))

    result = {
        "default": _normalise_quota_definition(default_source),
        "overrides": overrides,
    }
    return result


def normalise_memory_pointers(values: Optional[Sequence[Any]]) -> List[str]:
    return _clean_string_list(values)


class AgentRegistry(Base):
    __tablename__ = "agents_registry"
    __table_args__ = (
        UniqueConstraint("name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    module_path = Column(String(500), nullable=False)
    factory_function = Column(String(255), nullable=False)
    description = Column(Text)
    config_schema = Column(JSON)
    tools = Column(JSON)
    model_identifier = Column(String(255))
    provider = Column(String(100))
    system_prompt = Column(Text)
    memory_pointers = Column(JSON, nullable=False, default=default_memory_pointers)
    rollout_enabled = Column(Boolean, nullable=False, default=False)
    rollout_stage = Column(String(100))
    access_policies = Column(JSON, nullable=False, default=default_access_policies)
    quota_limits = Column(JSON, nullable=False, default=default_quota_limits)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    steps = relationship(
        "WorkflowStep",
        back_populates="agent",
    )

    @staticmethod
    def default_access_policies() -> Dict[str, Any]:
        return default_access_policies()

    @staticmethod
    def default_quota_limits() -> Dict[str, Any]:
        return default_quota_limits()

    @staticmethod
    def default_memory_pointers() -> List[str]:
        return default_memory_pointers()

    @staticmethod
    def normalize_access_policies(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        return normalise_access_policies(payload)

    @staticmethod
    def normalize_quota_limits(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        return normalise_quota_limits(payload)

    @staticmethod
    def normalize_memory_pointers(values: Optional[Sequence[Any]]) -> List[str]:
        return normalise_memory_pointers(values)
