"""Advanced async fixture helpers for test infrastructure.

This module provides utility functions and helpers for managing async operations,
global state, and complex fixture setup/teardown in tests.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

import pytest
import pytest_asyncio

logger = logging.getLogger(__name__)


# ============================================================================
# ASYNC CONTEXT MANAGERS
# ============================================================================

@asynccontextmanager
async def async_timeout(timeout_seconds: float = 5.0):
    """Context manager for async operations with timeout."""
    try:
        async with asyncio.timeout(timeout_seconds):
            yield
    except asyncio.TimeoutError:
        logger.error(f"Operation timed out after {timeout_seconds} seconds")
        raise


@asynccontextmanager
async def managed_background_tasks():
    """Context manager for managing background tasks in tests."""
    tasks: set = set()

    def create_task(coro):
        """Create a task and track it."""
        task = asyncio.create_task(coro)
        tasks.add(task)
        task.add_done_callback(tasks.discard)
        return task

    try:
        yield create_task
    finally:
        # Cancel all remaining tasks
        for task in tasks:
            if not task.done():
                task.cancel()

        # Wait for cancellation to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# ============================================================================
# FIXTURE HELPERS
# ============================================================================

async def reset_async_state():
    """Reset async state after test."""
    # Cancel all pending tasks
    try:
        loop = asyncio.get_running_loop()
        pending = asyncio.all_tasks(loop)
        for task in pending:
            if task and not task.done():
                task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
    except RuntimeError:
        pass

    # Allow cleanup
    await asyncio.sleep(0.001)


async def reset_cache_state():
    """Reset cache system state."""
    try:
        from src.core.multi_tier_cache import multi_tier_cache
        if multi_tier_cache:
            await multi_tier_cache.shutdown()
    except Exception as e:
        logger.debug(f"Cache reset error: {e}")


def reset_singletons():
    """Reset all singleton instances."""
    singletons = [
        ('src.core.vector_store', 'VectorStore', '_instance'),
        ('src.core.hybrid_retriever', 'HybridRetriever', '_instance'),
        ('src.core.retrieval_service', 'RetriovalService', '_instance'),
    ]

    for module_name, class_name, attr_name in singletons:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            if hasattr(cls, attr_name):
                setattr(cls, attr_name, None)
        except Exception as e:
            logger.debug(f"Singleton reset error for {class_name}: {e}")


def reset_global_state():
    """Reset global state variables."""
    # Reset task registries
    try:
        from src.api.routers.analysis import tasks
        tasks.clear()
    except Exception:
        pass

    try:
        from src.core.persistent_task_registry import persistent_task_registry
        persistent_task_registry.tasks.clear()
    except Exception:
        pass


# ============================================================================
# PYTEST FIXTURES FOR ASYNC HELPERS
# ============================================================================

@pytest_asyncio.fixture
async def async_timeout_fixture():
    """Fixture providing timeout context manager."""
    return async_timeout


@pytest_asyncio.fixture
async def background_task_manager():
    """Fixture providing managed background task creation."""
    async with managed_background_tasks() as task_creator:
        yield task_creator


@pytest.fixture
def reset_state():
    """Fixture to reset state before and after tests."""
    reset_singletons()
    reset_global_state()
    yield
    reset_singletons()
    reset_global_state()


@pytest_asyncio.fixture
async def async_cleanup():
    """Fixture for comprehensive async cleanup."""
    yield
    await reset_async_state()
    await reset_cache_state()


# ============================================================================
# MOCK HELPERS
# ============================================================================

def create_async_mock_retriever():
    """Create a mock HybridRetriever with async methods."""
    from unittest.mock import AsyncMock

    mock = AsyncMock()
    mock.retrieve = AsyncMock(return_value=[
        {
            'id': 'mock-1',
            'content': 'Mock retrieval result',
            'score': 0.95,
            'metadata': {}
        }
    ])
    mock.retrieve_by_tags = AsyncMock(return_value=[])
    mock.batch_retrieve = AsyncMock(return_value={})

    return mock


def create_async_mock_cache():
    """Create a mock MultiTierCacheSystem with async methods."""
    from unittest.mock import AsyncMock

    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock()
    mock.delete = AsyncMock()
    mock.clear = AsyncMock()
    mock.shutdown = AsyncMock()

    return mock


# ============================================================================
# CLEANUP UTILITIES
# ============================================================================

class AsyncCleanupManager:
    """Manager for cleanup of async resources."""

    def __init__(self):
        self.tasks: set = set()
        self.cleanup_callbacks: list = []

    def register_task(self, task: asyncio.Task):
        """Register a task for cleanup."""
        self.tasks.add(task)
        task.add_done_callback(lambda t: self.tasks.discard(t))

    def register_cleanup(self, callback):
        """Register a cleanup callback."""
        self.cleanup_callbacks.append(callback)

    async def cleanup(self):
        """Execute all cleanup operations."""
        # Cancel pending tasks
        for task in list(self.tasks):
            if not task.done():
                task.cancel()

        # Wait for cancellation
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Run cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.warning(f"Cleanup callback error: {e}")


@pytest_asyncio.fixture
async def cleanup_manager():
    """Fixture providing AsyncCleanupManager."""
    manager = AsyncCleanupManager()
    yield manager
    await manager.cleanup()
