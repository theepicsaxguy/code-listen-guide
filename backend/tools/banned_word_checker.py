"""Content safety helper that flags banned vocabulary."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable, List, Optional

from backend.tools import validate_tool_inputs, validate_tool_outputs


BANNED_WORD_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "banned_words": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Custom banned words to check",
        },
    },
    "required": ["text"],
}

BANNED_WORD_TOOL_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "has_match": {"type": "boolean"},
        "matches": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["has_match", "matches"],
}

_DEFAULT_BANNED_WORDS: List[str] = ["todo", "hack", "tmp"]


def _normalize(words: Iterable[str]) -> List[str]:
    return sorted({word.strip().lower() for word in words if word.strip()})


def _scan(text: str, banned_words: List[str]) -> List[str]:
    lower_text = text.lower()
    return [word for word in banned_words if word in lower_text]


def _ai_check_banned_words(text: str, banned_words: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Detect whether the provided text contains banned words."""

    validated_input = validate_tool_inputs(
        {"text": text, "banned_words": list(banned_words or [])},
        BANNED_WORD_TOOL_INPUT_SCHEMA,
    )
    words = _normalize(validated_input.get("banned_words", []) or _DEFAULT_BANNED_WORDS)
    matches = _scan(validated_input["text"], words)
    result = {"has_match": bool(matches), "matches": matches}
    validate_tool_outputs(result, BANNED_WORD_TOOL_OUTPUT_SCHEMA)
    return result


async def _ai_check_banned_words_async(
    text: str, banned_words: Optional[Iterable[str]] = None
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_check_banned_words`."""

    return await asyncio.to_thread(_ai_check_banned_words, text=text, banned_words=list(banned_words or []))
