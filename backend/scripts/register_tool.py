"""Register or update a tool registry entry from a callable."""

from __future__ import annotations

import argparse
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
from backend.models.tool_registry import ToolRegistry
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
    return parser.parse_args()


def _ensure_unique_name(session: Session, name: str, tool_id: Optional[UUID]) -> None:
    query = session.query(ToolRegistry).filter(ToolRegistry.name == name)
    if tool_id is not None:
        query = query.filter(ToolRegistry.id != tool_id)
    conflict = query.first()
    if conflict is not None:
        raise ValueError(f"Tool name '{name}' is already in use")


def _split_target(target: str) -> tuple[str, str]:
    if ":" not in target:
        raise ValueError("Target must be in module_path:function_name format")
    module_path, function_name = target.split(":", 1)
    if not module_path or not function_name:
        raise ValueError("Both module path and function name are required")
    return module_path, function_name


def main() -> int:
    args = _parse_args()
    module_path, function_name = _split_target(args.target)
    metadata = collect_tool_metadata(module_path, function_name)
    name = args.name or function_name
    with SessionLocal() as session:
        existing = (
            session.query(ToolRegistry)
            .filter(ToolRegistry.module_path == module_path)
            .filter(ToolRegistry.function_name == function_name)
            .one_or_none()
        )
        _ensure_unique_name(session, name, None if existing is None else existing.id)
        timestamp = datetime.utcnow()
        if existing is None:
            tool = ToolRegistry(
                name=name,
                module_path=module_path,
                function_name=function_name,
                description=args.description,
                input_schema=metadata.input_schema,
                output_schema=metadata.output_schema,
                signature_hash=metadata.signature_hash,
                input_schema_hash=metadata.input_schema_hash,
                output_schema_hash=metadata.output_schema_hash,
                last_validated_at=timestamp,
                last_validation_error=None,
            )
            session.add(tool)
            action = "created"
        else:
            existing.name = name
            if args.description is not None:
                existing.description = args.description
            existing.input_schema = metadata.input_schema
            existing.output_schema = metadata.output_schema
            existing.signature_hash = metadata.signature_hash
            existing.input_schema_hash = metadata.input_schema_hash
            existing.output_schema_hash = metadata.output_schema_hash
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
