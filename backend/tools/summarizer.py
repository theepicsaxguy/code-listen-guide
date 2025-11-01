"""Text summarization helpers for concise outputs."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from backend.tools import validate_tool_inputs, validate_tool_outputs


SUMMARIZER_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "sentence_count": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
            "default": 3,
        },
    },
    "required": ["text"],
}

SUMMARIZER_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "sentences_used": {"type": "integer"},
    },
    "required": ["summary", "sentences_used"],
}


def _split_sentences(text: str) -> list[str]:
    segments = [segment.strip() for segment in text.replace("\n", " ").split(".")]
    return [segment for segment in segments if segment]


def _ai_summarize(text: str, sentence_count: int = 3) -> Dict[str, Any]:
    """Return the first N sentences as a lightweight summary."""

    validated_input = validate_tool_inputs(
        {"text": text, "sentence_count": sentence_count}, SUMMARIZER_INPUT_SCHEMA
    )
    sentences = _split_sentences(validated_input["text"])
    count = min(len(sentences), validated_input.get("sentence_count", 3))
    selected = sentences[:count]
    summary = ". ".join(selected)
    if selected and not summary.endswith("."):
        summary = f"{summary}."
    result = {"summary": summary, "sentences_used": count}
    validate_tool_outputs(result, SUMMARIZER_OUTPUT_SCHEMA)
    return result


async def _ai_summarize_async(text: str, sentence_count: int = 3) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_summarize`."""

    return await asyncio.to_thread(_ai_summarize, text=text, sentence_count=sentence_count)
