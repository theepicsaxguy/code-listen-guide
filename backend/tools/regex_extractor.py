"""Regex extraction utilities for workflows."""

from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, Iterable, List, Optional

from backend.tools import validate_tool_inputs, validate_tool_outputs


REGEX_EXTRACTOR_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "pattern": {"type": "string"},
        "text": {"type": "string"},
        "flags": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["IGNORECASE", "MULTILINE", "DOTALL"],
            },
        },
    },
    "required": ["pattern", "text"],
}

REGEX_EXTRACTOR_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "matches": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
        "match_count": {"type": "integer"},
    },
    "required": ["matches", "match_count"],
}

_FLAG_MAP = {
    "IGNORECASE": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "DOTALL": re.DOTALL,
}


def _compile(pattern: str, flags: Optional[Iterable[str]]) -> re.Pattern[str]:
    flag_value = 0
    for flag_name in flags or []:
        flag_value |= _FLAG_MAP[flag_name]
    return re.compile(pattern, flag_value)


def _ai_regex_extract(pattern: str, text: str, flags: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Extract regex matches from text."""

    validated_input = validate_tool_inputs(
        {"pattern": pattern, "text": text, "flags": list(flags or [])},
        REGEX_EXTRACTOR_INPUT_SCHEMA,
    )
    compiled = _compile(validated_input["pattern"], validated_input.get("flags"))
    matches: List[List[str]] = [list(group) for group in compiled.findall(validated_input["text"])]
    result = {"matches": matches, "match_count": len(matches)}
    validate_tool_outputs(result, REGEX_EXTRACTOR_OUTPUT_SCHEMA)
    return result


async def _ai_regex_extract_async(
    pattern: str, text: str, flags: Optional[Iterable[str]] = None
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_regex_extract`."""

    return await asyncio.to_thread(
        _ai_regex_extract, pattern=pattern, text=text, flags=list(flags or [])
    )
