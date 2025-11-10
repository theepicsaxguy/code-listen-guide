"""Repository parsing plugin using chonkie pipeline.

This plugin provides pure functions for parsing and analyzing code repositories.
"""

from pathlib import Path
from typing import Any, Dict
from typing_extensions import Annotated
from pydantic import Field

from backend.services.chonkie_pipeline import chonkiePipeline


def parse_repository(
    path: Annotated[str, Field(description="Path to cloned repository root")],
) -> Dict[str, Any]:
    """Parse repository using chonkie pipeline.

    This function analyzes a code repository and returns structured metadata including:
    - File contents and chunks
    - Functions, classes, and imports
    - Dependency relationships
    - Language detection
    - Framework identification

    Args:
        path: Absolute path to the cloned repository root directory

    Returns:
        Dictionary containing:
        - repository_path: Path to the repository
        - modules: Dictionary mapping file paths to parsed data
        - summary: Aggregate statistics (file count, languages, etc.)
        - dependency_graph: File and function dependencies
        - execution_time_seconds: Processing time

    Note: This is a synchronous function that calls async code internally.
    Uses run_async_from_sync utility to safely handle event loop conflicts.
    """
    from backend.utils.async_runner import run_async_from_sync

    pipeline = chonkiePipeline()
    return run_async_from_sync(pipeline.process_pipeline, Path(path))


def parse_repository_with_filters(
    path: Annotated[str, Field(description="Path to cloned repository root")],
    include_patterns: Annotated[list[str] | None, Field(description="File patterns to include (e.g., ['*.py', '*.js'])")] = None,
    exclude_patterns: Annotated[list[str] | None, Field(description="Patterns to exclude (e.g., ['node_modules', '*.test.js'])")] = None,
) -> Dict[str, Any]:
    """Parse repository with custom include/exclude filters.

    This provides more control over which files are analyzed compared to parse_repository.

    Args:
        path: Absolute path to the cloned repository root directory
        include_patterns: File glob patterns to include (default: all common code files)
        exclude_patterns: Directory/file patterns to exclude (default: node_modules, .git, etc.)

    Returns:
        Same structure as parse_repository
    """
    from backend.utils.async_runner import run_async_from_sync

    pipeline = chonkiePipeline()
    return run_async_from_sync(
        pipeline.process_pipeline,
        Path(path),
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
    )
