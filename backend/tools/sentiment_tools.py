"""Simple rule-based sentiment analysis."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable, List

from backend.tools import validate_tool_inputs, validate_tool_outputs


SENTIMENT_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "positive_words": {
            "type": "array",
            "items": {"type": "string"},
        },
        "negative_words": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["text"],
}

SENTIMENT_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
        "score": {"type": "number"},
        "matches": {
            "type": "object",
            "properties": {
                "positive": {"type": "array", "items": {"type": "string"}},
                "negative": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["positive", "negative"],
        },
    },
    "required": ["sentiment", "score", "matches"],
}

_DEFAULT_POSITIVE: List[str] = ["great", "excellent", "love", "fantastic", "good"]
_DEFAULT_NEGATIVE: List[str] = ["bad", "poor", "hate", "terrible", "awful"]


def _collect_hits(text: str, words: Iterable[str]) -> List[str]:
    lower_text = text.lower()
    return [word for word in words if word in lower_text]


def _score(positive_hits: List[str], negative_hits: List[str]) -> float:
    return float(len(positive_hits) - len(negative_hits))


def _ai_analyze_sentiment(
    text: str,
    positive_words: Iterable[str] | None = None,
    negative_words: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Provide a coarse sentiment score based on keyword matches."""

    validated_input = validate_tool_inputs(
        {
            "text": text,
            "positive_words": list(positive_words or []),
            "negative_words": list(negative_words or []),
        },
        SENTIMENT_INPUT_SCHEMA,
    )
    positive_pool = validated_input.get("positive_words") or _DEFAULT_POSITIVE
    negative_pool = validated_input.get("negative_words") or _DEFAULT_NEGATIVE
    positive_hits = _collect_hits(validated_input["text"], positive_pool)
    negative_hits = _collect_hits(validated_input["text"], negative_pool)
    score_value = _score(positive_hits, negative_hits)
    if score_value > 0:
        sentiment = "positive"
    elif score_value < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    result = {
        "sentiment": sentiment,
        "score": score_value,
        "matches": {"positive": positive_hits, "negative": negative_hits},
    }
    validate_tool_outputs(result, SENTIMENT_OUTPUT_SCHEMA)
    return result


async def _ai_analyze_sentiment_async(
    text: str,
    positive_words: Iterable[str] | None = None,
    negative_words: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_analyze_sentiment`."""

    return await asyncio.to_thread(
        _ai_analyze_sentiment,
        text=text,
        positive_words=list(positive_words or []),
        negative_words=list(negative_words or []),
    )
