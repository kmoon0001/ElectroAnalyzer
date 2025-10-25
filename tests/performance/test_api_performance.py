"""Performance tests for API endpoints."""

import pytest
import time
import requests


def test_api_response_time():
    """Test API response time is acceptable."""
    start_time = time.time()
    response = requests.get("http://localhost:8001/health")
    execution_time = time.time() - start_time

    assert response.status_code == 200
    assert execution_time < 1.0  # Should respond within 1 second


def test_health_endpoint_performance():
    """Test health endpoint performance."""
    start_time = time.time()
    response = requests.get("http://localhost:8001/health/detailed")
    execution_time = time.time() - start_time

    assert response.status_code == 200
    assert execution_time < 2.0  # Detailed health check should be < 2 seconds


def test_docs_endpoint_performance():
    """Test API documentation endpoint performance."""
    start_time = time.time()
    response = requests.get("http://localhost:8001/docs")
    execution_time = time.time() - start_time

    assert response.status_code == 200
    assert execution_time < 3.0  # Docs should load within 3 seconds


@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test API handles concurrent requests well."""
    import asyncio
    import aiohttp

    async def make_request(session):
        async with session.get("http://localhost:8001/health") as response:
            return await response.json()

    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session) for _ in range(10)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        execution_time = time.time() - start_time

        # All requests should succeed
        assert len(results) == 10
        assert all(result is not None for result in results)
        # Concurrent requests should complete within reasonable time
        assert execution_time < 5.0
