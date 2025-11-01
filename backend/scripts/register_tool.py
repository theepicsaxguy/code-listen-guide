"""Register or update a tool registry entry from a callable."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.tool_registry import ToolRegistry, slugify_tool_name
from backend.workflows.tool_registry_validator import collect_tool_metadata


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Register or update a callable in the tool registry",
    )
    parser.add_argument(
        "target",
        help="Target callable in module_path:function_name form",
    )
    parser.add_argument("--name", help="Display name for the tool")
    parser.add_argument("--description", help="Optional description", default=None)
    parser.add_argument("--stable-slug", help="Stable slug identifier", default=None)
    parser.add_argument(
        "--semantic-version",
        help="Semantic version for this registration",
        default=None,
    )
    parser.add_argument("--owning-team", help="Owning team identifier", default=None)
    parser.add_argument(
        "--authorization-scope",
        help="Authorization scope for execution",
        default=None,
    )
    parser.add_argument(
        "--approval-mode",
        help="Approval mode (auto, manual, guarded)",
        default=None,
    )
    parser.add_argument(
        "--cost-profile",
        help="JSON object describing cost metadata",
        default=None,
    )
    return parser.parse_args()


def _ensure_unique_name(session: Session, name: str, tool_id: Optional[UUID]) -> None:
    query = session.query(ToolRegistry).filter(ToolRegistry.name == name)
    if tool_id is not None:
        query = query.filter(ToolRegistry.id != tool_id)
    conflict = query.first()
    if conflict is not None:
        raise ValueError(f"Tool name '{name}' is already in use")


def _ensure_unique_slug(
    session: Session, stable_slug: str, semantic_version: str, tool_id: Optional[UUID]
) -> None:
    query = (
        session.query(ToolRegistry)
        .filter(ToolRegistry.stable_slug == stable_slug)
        .filter(ToolRegistry.semantic_version == semantic_version)
    )
    if tool_id is not None:
        query = query.filter(ToolRegistry.id != tool_id)
    conflict = query.first()
    if conflict is not None:
        raise ValueError(
            f"Tool slug '{stable_slug}' with version '{semantic_version}' is already in use"
        )


def _split_target(target: str) -> tuple[str, str]:
    if ":" not in target:
        raise ValueError("Target must be in module_path:function_name format")
    module_path, function_name = target.split(":", 1)
    if not module_path or not function_name:
        raise ValueError("Both module path and function name are required")
    return module_path, function_name


def _parse_cost_profile(raw: Optional[str]) -> Optional[dict]:
    if raw is None:
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Cost profile must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("Cost profile must be a JSON object")
    return payload


def main() -> int:
    args = _parse_args()
    module_path, function_name = _split_target(args.target)
    metadata = collect_tool_metadata(module_path, function_name)
    name = args.name or function_name
    derived_slug = metadata.stable_slug
    derived_version = metadata.semantic_version
    derived_team = metadata.owning_team
    derived_scope = metadata.authorization_scope
    derived_approval = metadata.approval_mode
    derived_cost_profile = ToolRegistry.normalize_cost_profile(metadata.cost_profile)
    parsed_override = _parse_cost_profile(args.cost_profile)
    requested_cost_profile = (
        None
        if parsed_override is None
        else ToolRegistry.normalize_cost_profile(parsed_override)
    )
    stable_slug = slugify_tool_name(args.stable_slug or derived_slug or name)
    semantic_version = args.semantic_version or derived_version or "1.0.0"
    owning_team = args.owning_team or derived_team or "core-platform"
    authorization_scope = args.authorization_scope or derived_scope or "internal"
    approval_mode = args.approval_mode or derived_approval or "auto"
    cost_profile = requested_cost_profile or derived_cost_profile
    with SessionLocal() as session:
        existing = (
            session.query(ToolRegistry)
            .filter(ToolRegistry.module_path == module_path)
            .filter(ToolRegistry.function_name == function_name)
            .one_or_none()
        )
        tool_id = None if existing is None else existing.id
        _ensure_unique_name(session, name, tool_id)
        _ensure_unique_slug(session, stable_slug, semantic_version, tool_id)
        timestamp = datetime.utcnow()
        if existing is None:
            tool = ToolRegistry(
                name=name,
                stable_slug=stable_slug,
                semantic_version=semantic_version,
                module_path=module_path,
                function_name=function_name,
                description=args.description,
                input_schema=metadata.input_schema,
                output_schema=metadata.output_schema,
                signature_hash=metadata.signature_hash,
                input_schema_hash=metadata.input_schema_hash,
                output_schema_hash=metadata.output_schema_hash,
                owning_team=owning_team,
                authorization_scope=authorization_scope,
                approval_mode=approval_mode,
                cost_profile=cost_profile,
                last_validated_at=timestamp,
                last_validation_error=None,
            )
            session.add(tool)
            action = "created"
        else:
            existing.name = name
            existing.stable_slug = stable_slug
            existing.semantic_version = semantic_version
            if args.description is not None:
                existing.description = args.description
            existing.input_schema = metadata.input_schema
            existing.output_schema = metadata.output_schema
            existing.signature_hash = metadata.signature_hash
            existing.input_schema_hash = metadata.input_schema_hash
            existing.output_schema_hash = metadata.output_schema_hash
            existing.owning_team = owning_team
            existing.authorization_scope = authorization_scope
            existing.approval_mode = approval_mode
            existing.cost_profile = cost_profile
            existing.last_validated_at = timestamp
            existing.last_validation_error = None
            action = "updated"
        session.commit()
    print(f"✓ Tool '{name}' {action} from {module_path}:{function_name}")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        exit_code = 1
    raise SystemExit(exit_code)
