"""Timer utilities for workflow coordination."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from backend.tools import validate_tool_inputs, validate_tool_outputs


TIMER_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "start_time": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp in UTC",
        },
        "duration_seconds": {"type": "number", "minimum": 0},
        "label": {"type": "string"},
    },
}

TIMER_TOOL_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "label": {"type": "string"},
        "start_time": {"type": "string"},
        "end_time": {"type": "string"},
        "duration_seconds": {"type": "number"},
    },
    "required": ["label", "start_time", "end_time", "duration_seconds"],
}


def _parse_datetime(value: Optional[str]) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("start_time must be an ISO 8601 string") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _ai_timer(
    start_time: Optional[str] = None,
    duration_seconds: Optional[float] = None,
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a timer window with derived timestamps."""

    validated_input = validate_tool_inputs(
        {
            "start_time": start_time,
            "duration_seconds": duration_seconds,
            "label": label,
        },
        TIMER_TOOL_INPUT_SCHEMA,
    )
    start = _parse_datetime(validated_input.get("start_time"))
    duration = float(validated_input.get("duration_seconds", 0.0) or 0.0)
    end_time = start + timedelta(seconds=duration)
    result = {
        "label": validated_input.get("label") or "timer",
        "start_time": start.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
    }
    validate_tool_outputs(result, TIMER_TOOL_OUTPUT_SCHEMA)
    return result


async def _ai_timer_async(
    start_time: Optional[str] = None,
    duration_seconds: Optional[float] = None,
    label: Optional[str] = None,
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_timer`."""

    return await asyncio.to_thread(
        _ai_timer,
        start_time=start_time,
        duration_seconds=duration_seconds,
        label=label,
    )
