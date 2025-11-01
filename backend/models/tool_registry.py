"""SQLAlchemy model for registered tools/plugins available to agents."""

import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates

from backend.db.base import Base


def slugify_tool_name(value: str) -> str:
    normalized = value.strip().lower()
    collapsed = re.sub(r"[^a-z0-9]+", "-", normalized)
    trimmed = collapsed.strip("-")
    return trimmed or "tool"


def default_cost_profile(unit: str = "call", estimated_cost_usd: float = 0.0) -> Dict[str, Any]:
    return {"unit": unit, "estimated_cost_usd": estimated_cost_usd}


def build_core_tool(
    *,
    name: str,
    module_path: str,
    function_name: str,
    description: str,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    stable_slug: Optional[str] = None,
    semantic_version: str = "1.0.0",
    owning_team: str = "core-platform",
    authorization_scope: str = "internal",
    approval_mode: str = "auto",
    cost_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    slug_value = stable_slug or slugify_tool_name(name)
    payload: Dict[str, Any] = {
        "name": name,
        "stable_slug": slug_value,
        "semantic_version": semantic_version,
        "module_path": module_path,
        "function_name": function_name,
        "description": description,
        "schema_version": 1,
        "owning_team": owning_team,
        "authorization_scope": authorization_scope,
        "approval_mode": approval_mode,
        "cost_profile": cost_profile or default_cost_profile(),
    }
    if input_schema is not None:
        payload["input_schema"] = input_schema
    if output_schema is not None:
        payload["output_schema"] = output_schema
    return payload


class ToolRegistry(Base):
    __tablename__ = "tools_registry"
    __table_args__ = (
        UniqueConstraint("name"),
        UniqueConstraint(
            "module_path",
            "function_name",
            name="uq_tools_registry_module_path_function_name",
        ),
        UniqueConstraint(
            "stable_slug",
            "semantic_version",
            name="uq_tools_registry_slug_version",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    stable_slug = Column(String(255), nullable=False)
    semantic_version = Column(String(32), nullable=False, default="1.0.0")
    module_path = Column(String(500), nullable=False)
    function_name = Column(String(255), nullable=False)
    description = Column(Text)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    schema_version = Column(Integer, nullable=False, default=1)
    signature_hash = Column(String(128))
    input_schema_hash = Column(String(128))
    output_schema_hash = Column(String(128))
    owning_team = Column(String(255), nullable=False, default="core-platform")
    authorization_scope = Column(String(255), nullable=False, default="internal")
    approval_mode = Column(String(64), nullable=False, default="auto")
    cost_profile = Column(JSON, nullable=False, default=dict)
    cost_per_call_cents = Column(Integer)
    cost_per_1k_tokens_cents = Column(Integer)
    cost_per_second_cents = Column(Integer)
    cost_currency = Column(String(16))
    cost_provider = Column(String(255))
    last_validated_at = Column(DateTime)
    last_validation_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @staticmethod
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

    @classmethod
    def _extract_cost_fields(cls, payload: Mapping[str, Any]) -> Dict[str, Optional[Any]]:
        def _lookup(keys: List[str]) -> Optional[Any]:
            for candidate in keys:
                if candidate in payload and payload[candidate] is not None:
                    return payload[candidate]
            return None

        billing_block = payload.get("billing")
        billing_mapping: Mapping[str, Any] = billing_block if isinstance(billing_block, Mapping) else {}

        per_call = cls._coerce_cost_value(
            _lookup(["cost_per_call_cents", "costPerCallCents", "x-cost-per-call-cents"])
            or cls._coerce_cost_value(billing_mapping.get("cost_per_call_cents"))
        )
        per_tokens = cls._coerce_cost_value(
            _lookup(
                [
                    "cost_per_1k_tokens_cents",
                    "costPer1kTokensCents",
                    "x-cost-per-1k-tokens-cents",
                ]
            )
            or cls._coerce_cost_value(billing_mapping.get("cost_per_1k_tokens_cents"))
        )
        per_second = cls._coerce_cost_value(
            _lookup(["cost_per_second_cents", "costPerSecondCents", "x-cost-per-second-cents"])
            or cls._coerce_cost_value(billing_mapping.get("cost_per_second_cents"))
        )

        currency_candidate = _lookup(["currency", "cost_currency", "billing_currency"])
        if currency_candidate is None and isinstance(billing_mapping.get("currency"), str):
            currency_candidate = billing_mapping.get("currency")
        currency_value = currency_candidate.strip() if isinstance(currency_candidate, str) else None

        provider_candidate = _lookup(["provider", "vendor", "billing_provider"])
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

    @classmethod
    def normalize_cost_profile(cls, value: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if not value:
            return {}
        if not isinstance(value, Mapping):
            raise TypeError("cost_profile must be a mapping")
        normalized: Dict[str, Any] = {}
        for key, item in value.items():
            if isinstance(item, Mapping):
                normalized[key] = dict(item)
            else:
                normalized[key] = item
        extracted = cls._extract_cost_fields(normalized)
        for field, payload_value in extracted.items():
            if payload_value is not None:
                normalized[field] = payload_value
        return normalized

    @validates("cost_profile")
    def _sync_cost_columns(self, _key: str, value: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        normalized = self.normalize_cost_profile(value)
        extracted = self._extract_cost_fields(normalized)
        self.cost_per_call_cents = extracted["cost_per_call_cents"]
        self.cost_per_1k_tokens_cents = extracted["cost_per_1k_tokens_cents"]
        self.cost_per_second_cents = extracted["cost_per_second_cents"]
        currency = extracted["currency"]
        provider = extracted["provider"]
        has_pricing = any(
            metric is not None
            for metric in (
                self.cost_per_call_cents,
                self.cost_per_1k_tokens_cents,
                self.cost_per_second_cents,
            )
        )
        self.cost_currency = currency or ("USD" if has_pricing else None)
        self.cost_provider = provider
        return normalized

    def export_cost_profile(self) -> Dict[str, Any]:
        payload = self.normalize_cost_profile(self.cost_profile)
        if self.cost_per_call_cents is not None:
            payload["cost_per_call_cents"] = self.cost_per_call_cents
        if self.cost_per_1k_tokens_cents is not None:
            payload["cost_per_1k_tokens_cents"] = self.cost_per_1k_tokens_cents
        if self.cost_per_second_cents is not None:
            payload["cost_per_second_cents"] = self.cost_per_second_cents
        if self.cost_currency:
            payload["currency"] = self.cost_currency
        if self.cost_provider:
            payload["provider"] = self.cost_provider
        return {key: value for key, value in payload.items() if value is not None}


CORE_TOOL_REGISTRY_SEED_DATA: List[Dict[str, Any]] = [
    build_core_tool(
        name="clone_repository",
        module_path="backend.agents.analyzer_agent",
        function_name="_ai_clone_repo",
        description="Clone a Git repository into a temporary sandbox directory",
        input_schema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Git repository URL",
                }
            },
            "required": ["url"],
        },
        output_schema={
            "type": "string",
            "description": "Absolute path to the cloned repository",
        },
        cost_profile=default_cost_profile(unit="call", estimated_cost_usd=0.0),
    ),
    build_core_tool(
        name="list_repository_files",
        module_path="backend.agents.analyzer_agent",
        function_name="_ai_list_files",
        description="Return relative file paths contained in a cloned repository",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to cloned repository root",
                }
            },
            "required": ["path"],
        },
        output_schema={
            "type": "array",
            "items": {"type": "string"},
            "description": "Relative file paths in the repository",
        },
        cost_profile=default_cost_profile(unit="call", estimated_cost_usd=0.0),
    ),
    build_core_tool(
        name="parse_repository",
        module_path="backend.agents.analyzer_agent",
        function_name="_ai_parse_repository",
        description="Run the chonkie pipeline to analyse repository structure",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to cloned repository root",
                }
            },
            "required": ["path"],
        },
        output_schema={
            "type": "object",
            "description": "Structured repository analysis payload",
        },
        cost_profile=default_cost_profile(unit="call", estimated_cost_usd=0.0),
    ),
    build_core_tool(
        name="save_chapter_script",
        module_path="backend.agents.script_agent",
        function_name="_ai_save_script",
        description="Persist a generated narration script for a chapter",
        input_schema={
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Job identifier",
                },
                "chapter_number": {
                    "type": "integer",
                    "description": "Chapter index",
                },
                "script": {
                    "type": "string",
                    "description": "Narration script contents",
                },
            },
            "required": ["job_id", "chapter_number", "script"],
        },
        output_schema={
            "type": "boolean",
            "description": "True when the script is stored",
        },
        cost_profile=default_cost_profile(unit="call", estimated_cost_usd=0.0),
    ),
    build_core_tool(
        name="synthesize_speech",
        module_path="backend.agents.audio_agent",
        function_name="_ai_tts",
        description="Generate speech audio from text using the configured TTS provider",
        input_schema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to render as speech",
                },
                "voice": {
                    "type": "string",
                    "description": "Optional voice selection",
                },
            },
            "required": ["text"],
        },
        output_schema={
            "type": "string",
            "description": "Path to the generated audio file",
        },
        owning_team="audio-platform",
        approval_mode="guarded",
        cost_profile=default_cost_profile(unit="minute", estimated_cost_usd=0.12),
    ),
    build_core_tool(
        name="audio_upload_to_s3",
        module_path="backend.agents.audio_agent",
        function_name="_ai_upload",
        description="Upload synthesized chapter audio to object storage",
        input_schema={
            "type": "object",
            "properties": {
                "local_path": {
                    "type": "string",
                    "description": "Local file path to upload",
                },
                "s3_key": {
                    "type": "string",
                    "description": "Destination object key",
                },
            },
            "required": ["local_path", "s3_key"],
        },
        output_schema={
            "type": "string",
            "description": "Public URL of the uploaded object",
        },
        owning_team="audio-platform",
        cost_profile=default_cost_profile(unit="gigabyte", estimated_cost_usd=0.02),
    ),
    build_core_tool(
        name="concat_audio",
        module_path="backend.agents.postprocess_agent",
        function_name="_ai_concat",
        description="Merge chapter audio tracks into a single audiobook file",
        input_schema={
            "type": "object",
            "properties": {
                "chapter_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Audio file paths",
                },
                "chapter_titles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Chapter names",
                },
            },
            "required": ["chapter_paths", "chapter_titles"],
        },
        output_schema={
            "type": "object",
            "description": "Metadata for the merged audio artifact",
        },
        owning_team="audio-platform",
        approval_mode="guarded",
        cost_profile=default_cost_profile(unit="call", estimated_cost_usd=0.05),
    ),
]
