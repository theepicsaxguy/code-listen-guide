"""Lightweight knowledge base search helpers."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable, List, Mapping, Optional

from backend.tools import validate_tool_inputs, validate_tool_outputs


KNOWLEDGE_BASE_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {"type": "string"},
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["id", "text"],
            },
            "minItems": 1,
        },
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "default": 1,
        },
    },
    "required": ["query", "entries"],
}

KNOWLEDGE_BASE_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "matches": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "score": {"type": "number"},
                    "excerpt": {"type": "string"},
                },
                "required": ["id", "score", "excerpt"],
            },
        }
    },
    "required": ["matches"],
}


def _score_entry(query_tokens: List[str], entry_text: str) -> float:
    lower_text = entry_text.lower()
    hits = sum(1 for token in query_tokens if token in lower_text)
    return float(hits) / max(len(query_tokens), 1)


def _build_excerpt(entry_text: str, limit: int = 160) -> str:
    excerpt = entry_text.strip()
    if len(excerpt) <= limit:
        return excerpt
    return f"{excerpt[: limit - 3].rstrip()}..."


def _ai_query_knowledge_base(
    query: str,
    entries: Iterable[Mapping[str, str]],
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Return the best matching knowledge base entries for the query."""

    validated_input = validate_tool_inputs(
        {"query": query, "entries": list(entries), "limit": limit},
        KNOWLEDGE_BASE_INPUT_SCHEMA,
    )
    query_tokens = [token for token in validated_input["query"].lower().split() if token]
    ranked: List[Dict[str, Any]] = []
    for entry in validated_input["entries"]:
        score = _score_entry(query_tokens, entry["text"])
        if score == 0.0:
            continue
        ranked.append(
            {
                "id": entry["id"],
                "score": round(score, 4),
                "excerpt": _build_excerpt(entry["text"]),
            }
        )
    ranked.sort(key=lambda item: item["score"], reverse=True)
    top_n = validated_input.get("limit", 1)
    result = {"matches": ranked[:top_n]}
    validate_tool_outputs(result, KNOWLEDGE_BASE_OUTPUT_SCHEMA)
    return result


async def _ai_query_knowledge_base_async(
    query: str,
    entries: Iterable[Mapping[str, str]],
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_query_knowledge_base`."""

    return await asyncio.to_thread(
        _ai_query_knowledge_base, query=query, entries=list(entries), limit=limit
    )
