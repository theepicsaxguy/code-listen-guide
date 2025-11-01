"""Utility helpers used as Agent Framework tools."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from jsonschema import Draft7Validator


def _drop_none_values(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def validate_tool_inputs(payload: Mapping[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate tool inputs against the provided JSON schema."""

    cleaned = _drop_none_values(payload)
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(cleaned))
    if errors:
        messages = ", ".join(error.message for error in errors)
        raise ValueError(f"Invalid tool input: {messages}")
    return cleaned


def validate_tool_outputs(payload: Mapping[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate tool outputs against the provided JSON schema."""

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(payload))
    if errors:
        messages = ", ".join(error.message for error in errors)
        raise ValueError(f"Invalid tool output: {messages}")
    return dict(payload)
