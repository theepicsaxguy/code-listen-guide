"""Weather utility tools for deterministic calculations."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from backend.tools import validate_tool_inputs, validate_tool_outputs


WEATHER_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "temperature_c": {"type": "number"},
        "humidity": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
        },
        "wind_kph": {
            "type": "number",
            "minimum": 0,
        },
        "location": {"type": "string"},
    },
    "required": ["temperature_c", "humidity"],
}

WEATHER_TOOL_OUTPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "temperature_c": {"type": "number"},
        "humidity": {"type": "number"},
        "wind_kph": {"type": "number"},
        "feels_like_c": {"type": "number"},
        "dew_point_c": {"type": "number"},
        "heat_index_c": {"type": "number"},
    },
    "required": [
        "location",
        "temperature_c",
        "humidity",
        "wind_kph",
        "feels_like_c",
        "dew_point_c",
        "heat_index_c",
    ],
}


def _calculate_heat_index_c(temperature_c: float, humidity: float) -> float:
    temperature_f = temperature_c * 9.0 / 5.0 + 32.0
    hi = (
        -42.379
        + 2.04901523 * temperature_f
        + 10.14333127 * humidity
        - 0.22475541 * temperature_f * humidity
        - 0.00683783 * temperature_f**2
        - 0.05481717 * humidity**2
        + 0.00122874 * temperature_f**2 * humidity
        + 0.00085282 * temperature_f * humidity**2
        - 0.00000199 * temperature_f**2 * humidity**2
    )
    return (hi - 32.0) * 5.0 / 9.0


def _calculate_dew_point_c(temperature_c: float, humidity: float) -> float:
    import math

    a = 17.27
    b = 237.7
    alpha = ((a * temperature_c) / (b + temperature_c)) + math.log(humidity / 100.0)
    return (b * alpha) / (a - alpha)


def _calculate_feels_like_c(temperature_c: float, wind_kph: float) -> float:
    if wind_kph <= 4.8 or temperature_c >= 10.0:
        return temperature_c
    wind_ms = wind_kph / 3.6
    return 13.12 + 0.6215 * temperature_c - 11.37 * wind_ms ** 0.16 + 0.3965 * temperature_c * wind_ms ** 0.16


def _ai_weather_metrics(
    temperature_c: float,
    humidity: float,
    wind_kph: Optional[float] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """Derive weather comfort metrics from basic inputs."""

    validated_input = validate_tool_inputs(
        {
            "temperature_c": temperature_c,
            "humidity": humidity,
            "wind_kph": wind_kph,
            "location": location,
        },
        WEATHER_TOOL_INPUT_SCHEMA,
    )
    wind_speed = float(validated_input.get("wind_kph", 0.0) or 0.0)
    heat_index = _calculate_heat_index_c(float(validated_input["temperature_c"]), float(validated_input["humidity"]))
    dew_point = _calculate_dew_point_c(float(validated_input["temperature_c"]), float(validated_input["humidity"]))
    feels_like = _calculate_feels_like_c(float(validated_input["temperature_c"]), wind_speed)
    result = {
        "location": validated_input.get("location") or "Unknown",
        "temperature_c": float(validated_input["temperature_c"]),
        "humidity": float(validated_input["humidity"]),
        "wind_kph": wind_speed,
        "feels_like_c": feels_like,
        "dew_point_c": dew_point,
        "heat_index_c": heat_index,
    }
    validate_tool_outputs(result, WEATHER_TOOL_OUTPUT_SCHEMA)
    return result


async def _ai_weather_metrics_async(
    temperature_c: float,
    humidity: float,
    wind_kph: Optional[float] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """Asynchronous wrapper for :func:`_ai_weather_metrics`."""

    return await asyncio.to_thread(
        _ai_weather_metrics,
        temperature_c=temperature_c,
        humidity=humidity,
        wind_kph=wind_kph,
        location=location,
    )
