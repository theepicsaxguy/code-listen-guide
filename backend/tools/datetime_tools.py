"""Datetime utilities exposed as workflow tools."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from backend.tools import validate_tool_inputs, validate_tool_outputs


DATETIME_TOOL_INPUT_SCHEMA: Dict[str, object] = {
    "type": "object",
    "properties": {
        "timezone": {
            "type": "string",
            "description": "IANA timezone name such as 'UTC' or 'America/New_York'",
        },
        "format": {
            "type": "string",
            "description": "Optional strftime format string for the datetime field",
        },
    },
}

DATETIME_TOOL_OUTPUT_SCHEMA: Dict[str, object] = {
    "type": "object",
    "properties": {
        "timezone": {"type": "string"},
        "datetime": {"type": "string"},
        "unix_epoch": {"type": "number"},
    },
    "required": ["timezone", "datetime", "unix_epoch"],
}


def _resolve_timezone(name: Optional[str]) -> ZoneInfo:
    if not name:
        return ZoneInfo("UTC")
    try:
        return ZoneInfo(name)
    except Exception as exc:
        raise ValueError(f"Unknown timezone '{name}'") from exc


def _ai_get_datetime(timezone: Optional[str] = None, format: Optional[str] = None) -> Dict[str, Any]:
    """Return the current datetime for an optional timezone."""

    validated_input = validate_tool_inputs(
        {"timezone": timezone, "format": format}, DATETIME_TOOL_INPUT_SCHEMA
    )
    tz = _resolve_timezone(validated_input.get("timezone"))
    now = datetime.now(tz)
    display_format = validated_input.get("format")
    if display_format:
        try:
            formatted = now.strftime(display_format)
        except Exception as exc:
            raise ValueError(f"Invalid datetime format '{display_format}'") from exc
    else:
        formatted = now.isoformat()
    result = {
        "timezone": tz.key,
        "datetime": formatted,
        "unix_epoch": now.timestamp(),
    }
    validate_tool_outputs(result, DATETIME_TOOL_OUTPUT_SCHEMA)
    return result


async def _ai_get_datetime_async(timezone: Optional[str] = None, format: Optional[str] = None) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_get_datetime`."""

    return await asyncio.to_thread(_ai_get_datetime, timezone=timezone, format=format)
