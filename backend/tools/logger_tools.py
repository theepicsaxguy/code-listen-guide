"""Structured logging helpers for agents."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Mapping, Optional

from backend.tools import validate_tool_inputs, validate_tool_outputs


LOGGER_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "level": {
            "type": "string",
            "enum": ["debug", "info", "warning", "error", "critical"],
            "default": "info",
        },
        "message": {"type": "string"},
        "context": {"type": "object"},
    },
    "required": ["message"],
}

LOGGER_TOOL_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "logged": {"type": "boolean"},
        "level": {"type": "string"},
    },
    "required": ["logged", "level"],
}

_LOGGER = logging.getLogger("backend.tools.logger")


def _log(level: str, message: str, context: Optional[Mapping[str, Any]]) -> None:
    if context:
        serialized = json.dumps(context, sort_keys=True)
        composed = f"{message} | context={serialized}"
    else:
        composed = message
    _LOGGER.log(getattr(logging, level.upper()), composed)


def _ai_log_message(
    message: str,
    level: str = "info",
    context: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Emit a structured log message."""

    validated_input = validate_tool_inputs(
        {"message": message, "level": level, "context": context}, LOGGER_TOOL_INPUT_SCHEMA
    )
    _log(validated_input.get("level", "info"), validated_input["message"], validated_input.get("context"))
    result = {"logged": True, "level": validated_input.get("level", "info")}
    validate_tool_outputs(result, LOGGER_TOOL_OUTPUT_SCHEMA)
    return result


async def _ai_log_message_async(
    message: str,
    level: str = "info",
    context: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_log_message`."""

    return await asyncio.to_thread(_ai_log_message, message=message, level=level, context=context)
