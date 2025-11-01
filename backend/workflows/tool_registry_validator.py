"""Utilities for validating and introspecting registered tools."""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, Optional
import typing
from uuid import UUID

from pydantic import TypeAdapter, create_model
from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.tool_registry import ToolRegistry, slugify_tool_name


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolIntrospection:
    module_path: str
    function_name: str
    signature_hash: str
    input_schema: Dict[str, Any]
    input_schema_hash: str
    output_schema: Dict[str, Any]
    output_schema_hash: str
    stable_slug: str
    semantic_version: str
    owning_team: str
    authorization_scope: str
    approval_mode: str
    cost_profile: Dict[str, Any]


@dataclass(frozen=True)
class ToolValidationResult:
    tool_id: UUID
    name: str
    module_path: str
    function_name: str
    is_valid: bool
    issues: tuple[str, ...]
    stored_signature_hash: Optional[str]
    derived_signature_hash: Optional[str]
    stored_input_hash: Optional[str]
    derived_input_hash: Optional[str]
    stored_output_hash: Optional[str]
    derived_output_hash: Optional[str]


class ToolValidationError(RuntimeError):
    """Raised when tool validation fails."""

    def __init__(self, failures: Iterable[ToolValidationResult]):
        issues = [
            f"{result.name} ({result.module_path}.{result.function_name}): {', '.join(result.issues)}"
            for result in failures
        ]
        message = "; ".join(issues)
        super().__init__(message)


def load_tool_callable(module_path: str, function_name: str) -> Callable[..., Any]:
    module = importlib.import_module(module_path)
    candidate = getattr(module, function_name, None)
    if candidate is None:
        raise AttributeError(f"Function '{function_name}' not found in module '{module_path}'")
    if not callable(candidate):
        raise TypeError(f"Attribute '{function_name}' in module '{module_path}' is not callable")
    return candidate


def _schema_hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _signature_hash(func: Callable[..., Any]) -> str:
    signature = inspect.signature(func)
    qualified = f"{func.__module__}.{func.__qualname__}{signature}"
    return hashlib.sha256(qualified.encode("utf-8")).hexdigest()


def _build_input_schema(func: Callable[..., Any]) -> Dict[str, Any]:
    signature = inspect.signature(func)
    annotations = typing.get_type_hints(func, include_extras=True)
    fields: Dict[str, tuple[Any, Any]] = {}
    for name, parameter in signature.parameters.items():
        if parameter.kind not in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            raise TypeError(
                f"Unsupported parameter kind for '{name}' in {func.__module__}.{func.__qualname__}"
            )
        annotation = annotations.get(name, Any)
        default = parameter.default if parameter.default is not inspect._empty else ...
        fields[name] = (annotation, default)
    model_name = f"{func.__name__.title()}Input"
    input_model = create_model(model_name, **fields)
    return input_model.model_json_schema()


def _build_output_schema(func: Callable[..., Any]) -> Dict[str, Any]:
    annotations = typing.get_type_hints(func, include_extras=True)
    return_annotation = annotations.get("return", Any)
    adapter = TypeAdapter(return_annotation)
    return adapter.json_schema()


def _load_declared_metadata(func: Callable[..., Any]) -> Dict[str, Any]:
    candidate = getattr(func, "__registry_metadata__", None)
    if candidate is None:
        candidate = getattr(func, "__tool_metadata__", None)
    module = inspect.getmodule(func)
    if (candidate is None or not isinstance(candidate, dict)) and module is not None:
        container = getattr(module, "TOOL_METADATA", None)
        if isinstance(container, dict):
            candidate = container.get(func.__name__)
        if candidate is None:
            registry_container = getattr(module, "TOOL_REGISTRY_METADATA", None)
            if isinstance(registry_container, dict):
                candidate = registry_container.get(func.__name__)
    if isinstance(candidate, dict):
        return candidate
    return {}


def _derive_registry_metadata(func: Callable[..., Any], fallback_name: str) -> Dict[str, Any]:
    declared = _load_declared_metadata(func)
    slug_source = declared.get("stable_slug") or declared.get("name") or fallback_name
    stable_slug = slugify_tool_name(slug_source)
    semantic_version = declared.get("semantic_version", "1.0.0")
    owning_team = declared.get("owning_team", "core-platform")
    authorization_scope = declared.get("authorization_scope", "internal")
    approval_mode = declared.get("approval_mode", "auto")
    cost_profile = ToolRegistry.normalize_cost_profile(declared.get("cost_profile"))
    return {
        "stable_slug": stable_slug,
        "semantic_version": semantic_version,
        "owning_team": owning_team,
        "authorization_scope": authorization_scope,
        "approval_mode": approval_mode,
        "cost_profile": cost_profile,
    }


def collect_tool_metadata(module_path: str, function_name: str) -> ToolIntrospection:
    func = load_tool_callable(module_path, function_name)
    input_schema = _build_input_schema(func)
    output_schema = _build_output_schema(func)
    signature_hash = _signature_hash(func)
    input_schema_hash = _schema_hash(input_schema)
    output_schema_hash = _schema_hash(output_schema)
    registry_metadata = _derive_registry_metadata(func, function_name)
    return ToolIntrospection(
        module_path=module_path,
        function_name=function_name,
        signature_hash=signature_hash,
        input_schema=input_schema,
        input_schema_hash=input_schema_hash,
        output_schema=output_schema,
        output_schema_hash=output_schema_hash,
        stable_slug=registry_metadata["stable_slug"],
        semantic_version=registry_metadata["semantic_version"],
        owning_team=registry_metadata["owning_team"],
        authorization_scope=registry_metadata["authorization_scope"],
        approval_mode=registry_metadata["approval_mode"],
        cost_profile=registry_metadata["cost_profile"],
    )


def _normalize_schema(schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if schema is None:
        return {}
    return schema


def _validate_tool(tool: ToolRegistry, timestamp: datetime) -> ToolValidationResult:
    issues: list[str] = []
    derived: Optional[ToolIntrospection] = None
    try:
        derived = collect_tool_metadata(tool.module_path, tool.function_name)
    except Exception as exc:
        issues.append(str(exc))
        logger.exception(
            "Failed to introspect tool %s.%s",
            tool.module_path,
            tool.function_name,
        )
    else:
        if not tool.signature_hash:
            issues.append("missing signature hash")
        elif tool.signature_hash != derived.signature_hash:
            issues.append("signature hash mismatch")
        if _normalize_schema(tool.input_schema) != derived.input_schema:
            issues.append("stored input schema differs from callable")
        if not tool.input_schema_hash:
            issues.append("missing input schema hash")
        elif tool.input_schema_hash != derived.input_schema_hash:
            issues.append("input schema hash mismatch")
        if _normalize_schema(tool.output_schema) != derived.output_schema:
            issues.append("stored output schema differs from callable")
        if not tool.output_schema_hash:
            issues.append("missing output schema hash")
        elif tool.output_schema_hash != derived.output_schema_hash:
            issues.append("output schema hash mismatch")
        if tool.stable_slug != derived.stable_slug:
            issues.append("stable slug mismatch")
        if tool.semantic_version != derived.semantic_version:
            issues.append("semantic version mismatch")
        if tool.owning_team != derived.owning_team:
            issues.append("owning team mismatch")
        if tool.authorization_scope != derived.authorization_scope:
            issues.append("authorization scope mismatch")
        if tool.approval_mode != derived.approval_mode:
            issues.append("approval mode mismatch")
        if ToolRegistry.normalize_cost_profile(tool.cost_profile) != derived.cost_profile:
            issues.append("cost profile mismatch")
    tool.last_validated_at = timestamp
    tool.last_validation_error = None if not issues else "; ".join(issues)
    return ToolValidationResult(
        tool_id=tool.id,
        name=tool.name,
        module_path=tool.module_path,
        function_name=tool.function_name,
        is_valid=not issues,
        issues=tuple(issues),
        stored_signature_hash=tool.signature_hash,
        derived_signature_hash=None if derived is None else derived.signature_hash,
        stored_input_hash=tool.input_schema_hash,
        derived_input_hash=None if derived is None else derived.input_schema_hash,
        stored_output_hash=tool.output_schema_hash,
        derived_output_hash=None if derived is None else derived.output_schema_hash,
    )


def validate_registered_tools(raise_on_error: bool = False) -> list[ToolValidationResult]:
    with SessionLocal() as session:
        results = _validate_with_session(session)
        session.commit()
    failures = [result for result in results if not result.is_valid]
    if raise_on_error and failures:
        raise ToolValidationError(failures)
    return results


def _validate_with_session(session: Session) -> list[ToolValidationResult]:
    tools: list[ToolRegistry] = (
        session.query(ToolRegistry).order_by(ToolRegistry.name.asc()).all()
    )
    timestamp = datetime.utcnow()
    results: list[ToolValidationResult] = []
    for tool in tools:
        results.append(_validate_tool(tool, timestamp))
    return results
