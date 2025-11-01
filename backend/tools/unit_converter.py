"""Deterministic unit conversion helpers."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from backend.tools import validate_tool_inputs, validate_tool_outputs


UNIT_CONVERTER_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "value": {"type": "number"},
        "from_unit": {"type": "string"},
        "to_unit": {"type": "string"},
    },
    "required": ["value", "from_unit", "to_unit"],
}

UNIT_CONVERTER_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "value": {"type": "number"},
        "from_unit": {"type": "string"},
        "to_unit": {"type": "string"},
        "converted_value": {"type": "number"},
    },
    "required": ["value", "from_unit", "to_unit", "converted_value"],
}

_UNIT_FACTORS: Dict[str, float] = {
    "meter": 1.0,
    "kilometer": 1000.0,
    "centimeter": 0.01,
    "mile": 1609.34,
    "foot": 0.3048,
    "inch": 0.0254,
    "kilogram": 1.0,
    "gram": 0.001,
    "pound": 0.453592,
    "ounce": 0.0283495,
}


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    if from_unit == to_unit:
        return value
    if from_unit == "celsius" and to_unit == "fahrenheit":
        return value * 9.0 / 5.0 + 32.0
    if from_unit == "fahrenheit" and to_unit == "celsius":
        return (value - 32.0) * 5.0 / 9.0
    if from_unit == "celsius" and to_unit == "kelvin":
        return value + 273.15
    if from_unit == "kelvin" and to_unit == "celsius":
        return value - 273.15
    if from_unit == "fahrenheit" and to_unit == "kelvin":
        return (value + 459.67) * 5.0 / 9.0
    if from_unit == "kelvin" and to_unit == "fahrenheit":
        return value * 9.0 / 5.0 - 459.67
    raise ValueError(f"Unsupported temperature conversion from {from_unit} to {to_unit}")


def _convert(value: float, from_unit: str, to_unit: str) -> float:
    lower_from = from_unit.lower()
    lower_to = to_unit.lower()
    if lower_from in {"celsius", "fahrenheit", "kelvin"}:
        return _convert_temperature(value, lower_from, lower_to)
    if lower_from not in _UNIT_FACTORS or lower_to not in _UNIT_FACTORS:
        raise ValueError(f"Unsupported units: {from_unit} -> {to_unit}")
    base_value = value * _UNIT_FACTORS[lower_from]
    return base_value / _UNIT_FACTORS[lower_to]


def _ai_convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """Convert a numeric value between supported units."""

    validated_input = validate_tool_inputs(
        {"value": value, "from_unit": from_unit, "to_unit": to_unit},
        UNIT_CONVERTER_INPUT_SCHEMA,
    )
    converted_value = _convert(
        float(validated_input["value"]),
        validated_input["from_unit"],
        validated_input["to_unit"],
    )
    result = {
        "value": float(validated_input["value"]),
        "from_unit": validated_input["from_unit"],
        "to_unit": validated_input["to_unit"],
        "converted_value": converted_value,
    }
    validate_tool_outputs(result, UNIT_CONVERTER_OUTPUT_SCHEMA)
    return result


async def _ai_convert_units_async(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_convert_units`."""

    return await asyncio.to_thread(_ai_convert_units, value=value, from_unit=from_unit, to_unit=to_unit)
