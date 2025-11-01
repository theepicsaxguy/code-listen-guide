"""Content moderation helpers for lightweight policy enforcement."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable, List

from backend.tools import validate_tool_inputs, validate_tool_outputs


MODERATION_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "categories": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Custom moderation categories",
        },
    },
    "required": ["text"],
}

MODERATION_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "flagged": {"type": "boolean"},
        "categories": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["flagged", "categories"],
}

_DEFAULT_CATEGORIES: Dict[str, List[str]] = {
    "self_harm": ["suicide", "self-harm"],
    "violence": ["kill", "attack", "threat"],
    "adult": ["explicit", "nsfw", "adult"],
}


def _scan_categories(text: str, categories: Iterable[str]) -> List[str]:
    lower_text = text.lower()
    matched: List[str] = []
    for category in categories:
        keywords = _DEFAULT_CATEGORIES.get(category, [])
        if any(keyword in lower_text for keyword in keywords):
            matched.append(category)
    return matched


def _ai_moderate_text(text: str, categories: Iterable[str] | None = None) -> Dict[str, Any]:
    """Check text against basic moderation categories."""

    validated_input = validate_tool_inputs(
        {"text": text, "categories": list(categories or [])}, MODERATION_INPUT_SCHEMA
    )
    requested = validated_input.get("categories") or list(_DEFAULT_CATEGORIES.keys())
    matches = _scan_categories(validated_input["text"], requested)
    result = {"flagged": bool(matches), "categories": matches}
    validate_tool_outputs(result, MODERATION_OUTPUT_SCHEMA)
    return result


async def _ai_moderate_text_async(
    text: str, categories: Iterable[str] | None = None
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_moderate_text`."""

    return await asyncio.to_thread(_ai_moderate_text, text=text, categories=list(categories or []))
