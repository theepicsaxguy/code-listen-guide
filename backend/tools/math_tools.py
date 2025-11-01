"""Math utilities exposed as workflow tools."""

from __future__ import annotations

import asyncio
from statistics import mean
from typing import Any, Dict, Iterable, List

from backend.tools import validate_tool_inputs, validate_tool_outputs


MATH_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "operation": {
            "type": "string",
            "enum": ["add", "subtract", "multiply", "divide", "average"],
            "description": "Math operation to perform",
        },
        "values": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 1,
        },
    },
    "required": ["operation", "values"],
}

MATH_TOOL_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "operation": {"type": "string"},
        "values": {"type": "array", "items": {"type": "number"}},
        "result": {"type": "number"},
    },
    "required": ["operation", "values", "result"],
}


def _require_values(values: Iterable[float]) -> List[float]:
    numbers = [float(value) for value in values]
    if not numbers:
        raise ValueError("At least one numeric value is required")
    return numbers


def _perform_operation(operation: str, numbers: List[float]) -> float:
    if operation == "add":
        return sum(numbers)
    if operation == "subtract":
        head, *tail = numbers
        return head - sum(tail)
    if operation == "multiply":
        result = 1.0
        for value in numbers:
            result *= value
        return result
    if operation == "divide":
        head, *tail = numbers
        result = head
        for value in tail:
            if value == 0:
                raise ValueError("Division by zero is not allowed")
            result /= value
        return result
    if operation == "average":
        return mean(numbers)
    raise ValueError(f"Unsupported math operation '{operation}'")


def _ai_calculate(operation: str, values: Iterable[float]) -> Dict[str, Any]:
    """Execute a basic math operation on the provided values."""

    validated_input = validate_tool_inputs(
        {"operation": operation, "values": list(values)}, MATH_TOOL_INPUT_SCHEMA
    )
    numbers = _require_values(validated_input["values"])
    result_value = _perform_operation(validated_input["operation"], numbers)
    result = {
        "operation": validated_input["operation"],
        "values": numbers,
        "result": result_value,
    }
    validate_tool_outputs(result, MATH_TOOL_OUTPUT_SCHEMA)
    return result


async def _ai_calculate_async(operation: str, values: Iterable[float]) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_calculate`."""

    return await asyncio.to_thread(_ai_calculate, operation=operation, values=list(values))
