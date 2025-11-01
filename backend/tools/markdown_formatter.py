"""Markdown formatting helpers."""

from __future__ import annotations

import asyncio
from textwrap import indent
from typing import Any, Dict, Iterable, Optional

from backend.tools import validate_tool_inputs, validate_tool_outputs


MARKDOWN_FORMATTER_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "style": {
            "type": "string",
            "enum": ["paragraph", "bullet", "numbered", "quote", "code"],
            "default": "paragraph",
        },
        "language": {"type": "string"},
    },
    "required": ["content"],
}

MARKDOWN_FORMATTER_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "markdown": {"type": "string"},
    },
    "required": ["markdown"],
}


def _format_bullet(lines: Iterable[str]) -> str:
    return "\n".join(f"- {line.strip()}" for line in lines if line.strip())


def _format_numbered(lines: Iterable[str]) -> str:
    enumerated = []
    for index, line in enumerate(lines, start=1):
        clean = line.strip()
        if clean:
            enumerated.append(f"{index}. {clean}")
    return "\n".join(enumerated)


def _format_quote(content: str) -> str:
    return indent(content.strip(), "> ")


def _format_code(content: str, language: Optional[str]) -> str:
    lang = language or ""
    return f"```{lang}\n{content.rstrip()}\n```"


def _ai_format_markdown(
    content: str,
    style: str = "paragraph",
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """Render text into a specific markdown style."""

    validated_input = validate_tool_inputs(
        {"content": content, "style": style, "language": language},
        MARKDOWN_FORMATTER_INPUT_SCHEMA,
    )
    style_name = validated_input.get("style", "paragraph")
    if style_name == "paragraph":
        markdown = validated_input["content"].strip()
    elif style_name == "bullet":
        markdown = _format_bullet(validated_input["content"].splitlines())
    elif style_name == "numbered":
        markdown = _format_numbered(validated_input["content"].splitlines())
    elif style_name == "quote":
        markdown = _format_quote(validated_input["content"])
    elif style_name == "code":
        markdown = _format_code(validated_input["content"], validated_input.get("language"))
    else:
        raise ValueError(f"Unsupported markdown style '{style_name}'")
    result = {"markdown": markdown}
    validate_tool_outputs(result, MARKDOWN_FORMATTER_OUTPUT_SCHEMA)
    return result


async def _ai_format_markdown_async(
    content: str,
    style: str = "paragraph",
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_format_markdown`."""

    return await asyncio.to_thread(
        _ai_format_markdown, content=content, style=style, language=language
    )
