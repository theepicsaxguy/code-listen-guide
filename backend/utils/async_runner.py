"""Utility for running async code from synchronous contexts.

This module provides utilities to safely run async functions from synchronous
tool functions (e.g., Agent Framework tools) that may be called from async contexts.
"""

import asyncio
import logging
import threading
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def run_async_from_sync(coro: Callable[..., Any], *args, **kwargs) -> Any:
    """
    Run an async coroutine from a synchronous context, handling event loop conflicts.
    
    This function safely handles cases where:
    1. We're already in an async context (e.g., FastAPI request handler)
    2. We're in a sync context (e.g., tool function)
    
    Args:
        coro: Async coroutine function or coroutine object to run
        *args: Positional arguments to pass to the coroutine
        **kwargs: Keyword arguments to pass to the coroutine
    
    Returns:
        The result of the coroutine execution
    
    Example:
        ```python
        async def my_async_function(path: str) -> dict:
            # ... async operations
            return result
        
        def sync_tool_function(path: str) -> dict:
            return run_async_from_sync(my_async_function, path)
        ```
    """
    # Check if coro is a coroutine function (needs to be called) or coroutine object
    if asyncio.iscoroutine(coro):
        # It's already a coroutine object
        coroutine = coro
    elif asyncio.iscoroutinefunction(coro):
        # It's a coroutine function, need to call it
        coroutine = coro(*args, **kwargs)
    else:
        # Assume it's a callable that returns a coroutine
        coroutine = coro(*args, **kwargs)
    
    # Check if we're already in an async context
    try:
        asyncio.get_running_loop()
        # We're in an async context - run in separate thread to avoid conflicts
        result_container: dict[str, Any] = {}
        exception_container: dict[str, Exception] = {}
        
        def run_in_thread():
            """Run async code in a new thread with its own event loop."""
            try:
                # Create new event loop in this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(coroutine)
                    result_container['result'] = result
                finally:
                    new_loop.close()
            except Exception as e:
                logger.exception(f"Error running async code in thread: {e}")
                exception_container['exception'] = e
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        thread.join()
        
        if exception_container:
            raise exception_container['exception']
        return result_container['result']
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        return asyncio.run(coroutine)

