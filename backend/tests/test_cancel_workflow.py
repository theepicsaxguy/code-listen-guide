"""Tests for workflow cancellation functionality.

These tests validate the cancel_workflow function without requiring
database migrations.
"""
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest

# Mock OpenTelemetry before importing
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

trace_module = ModuleType("opentelemetry.trace")
trace_module.get_tracer = lambda name: MagicMock()
opentelemetry_module = ModuleType("opentelemetry")
opentelemetry_module.trace = trace_module
sys.modules.setdefault("opentelemetry.trace", trace_module)
sys.modules.setdefault("opentelemetry", opentelemetry_module)

from backend.tasks import audiobook_tasks


def test_cancel_workflow_with_active_workflow():
    """Test cancelling an active workflow."""
    workflow = MagicMock()
    workflow.cancel = MagicMock()
    
    # Register workflow
    with audiobook_tasks._workflows_lock:
        audiobook_tasks._active_workflows["job-123"] = workflow
    
    try:
        result = audiobook_tasks.cancel_workflow("job-123")
        
        assert result is True
        workflow.cancel.assert_called_once()
    finally:
        # Cleanup
        with audiobook_tasks._workflows_lock:
            audiobook_tasks._active_workflows.pop("job-123", None)


def test_cancel_workflow_without_active_workflow():
    """Test cancelling when no workflow is active."""
    result = audiobook_tasks.cancel_workflow("job-nonexistent")
    
    assert result is False


def test_cancel_workflow_handles_exception():
    """Test cancel_workflow handles exceptions gracefully."""
    workflow = MagicMock()
    workflow.cancel = MagicMock(side_effect=Exception("Test error"))
    
    # Register workflow
    with audiobook_tasks._workflows_lock:
        audiobook_tasks._active_workflows["job-456"] = workflow
    
    try:
        result = audiobook_tasks.cancel_workflow("job-456")
        
        assert result is False
        workflow.cancel.assert_called_once()
    finally:
        # Cleanup
        with audiobook_tasks._workflows_lock:
            audiobook_tasks._active_workflows.pop("job-456", None)


def test_workflow_registry_isolation():
    """Test that workflow registry operations are thread-safe."""
    workflow1 = MagicMock()
    workflow2 = MagicMock()
    
    # Register multiple workflows
    with audiobook_tasks._workflows_lock:
        audiobook_tasks._active_workflows["job-a"] = workflow1
        audiobook_tasks._active_workflows["job-b"] = workflow2
    
    try:
        # Verify both are registered
        with audiobook_tasks._workflows_lock:
            assert "job-a" in audiobook_tasks._active_workflows
            assert "job-b" in audiobook_tasks._active_workflows
        
        # Cancel one should not affect the other
        audiobook_tasks.cancel_workflow("job-a")
        
        with audiobook_tasks._workflows_lock:
            assert "job-a" in audiobook_tasks._active_workflows  # Still there
            assert "job-b" in audiobook_tasks._active_workflows
    finally:
        # Cleanup
        with audiobook_tasks._workflows_lock:
            audiobook_tasks._active_workflows.pop("job-a", None)
            audiobook_tasks._active_workflows.pop("job-b", None)
