"""Background job that monitors tool registry integrity."""

from __future__ import annotations

import asyncio
import logging
from typing import Sequence

from backend.workflows.tool_registry_validator import (
    ToolValidationResult,
    validate_registered_tools,
)


logger = logging.getLogger(__name__)


async def _wait_or_stop(stop_event: asyncio.Event, timeout: float) -> None:
    try:
        await asyncio.wait_for(stop_event.wait(), timeout)
    except asyncio.TimeoutError:
        return


def _log_results(results: Sequence[ToolValidationResult]) -> None:
    if not results:
        logger.info("Tool registry validation completed: no registered tools found")
        return
    failures = [result for result in results if not result.is_valid]
    if not failures:
        logger.info("Tool registry validation passed for %s tool(s)", len(results))
        return
    for failure in failures:
        logger.warning(
            "Tool drift detected for %s (%s.%s): %s",
            failure.name,
            failure.module_path,
            failure.function_name,
            "; ".join(failure.issues),
        )


async def tool_registry_integrity_loop(
    interval_seconds: int,
    stop_event: asyncio.Event,
) -> None:
    logger.info(
        "Tool registry integrity loop started with interval %s seconds",
        interval_seconds,
    )
    try:
        while not stop_event.is_set():
            results = validate_registered_tools(raise_on_error=False)
            _log_results(results)
            await _wait_or_stop(stop_event, interval_seconds)
    except asyncio.CancelledError:
        logger.info("Tool registry integrity loop cancelled")
        raise
    finally:
        logger.info("Tool registry integrity loop stopped")
