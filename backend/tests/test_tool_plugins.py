from __future__ import annotations

from backend.tools.datetime_tools import _ai_get_datetime
from backend.tools.logger_tools import _ai_log_message
from backend.tools.markdown_formatter import _ai_format_markdown
from backend.tools.math_tools import _ai_calculate
from backend.tools.moderation_tools import _ai_moderate_text
from backend.tools.unit_converter import _ai_convert_units


def test_datetime_tool_returns_expected_fields() -> None:
    result = _ai_get_datetime(timezone="UTC")
    assert result["timezone"] == "UTC"
    assert "datetime" in result
    assert result["unix_epoch"] > 0


def test_math_tool_handles_division() -> None:
    result = _ai_calculate("divide", [20, 2, 2])
    assert result["result"] == 5


def test_moderation_flags_keywords() -> None:
    result = _ai_moderate_text("This is an explicit spoiler")
    assert result["flagged"] is True
    assert "adult" in result["categories"]


def test_unit_converter_temperature_round_trip() -> None:
    fahrenheit = _ai_convert_units(0, "celsius", "fahrenheit")
    back_to_celsius = _ai_convert_units(fahrenheit["converted_value"], "fahrenheit", "celsius")
    assert round(back_to_celsius["converted_value"], 5) == 0


def test_markdown_formatter_bullet_style() -> None:
    content = "item one\nitem two"
    result = _ai_format_markdown(content, style="bullet")
    assert result["markdown"] == "- item one\n- item two"


def test_logger_tool_returns_metadata() -> None:
    result = _ai_log_message("hello", level="info", context={"value": 1})
    assert result == {"logged": True, "level": "info"}
