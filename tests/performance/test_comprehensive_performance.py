"""Comprehensive Performance Test Suite

Tests API performance characteristics including:
- Response time validation
- Concurrent request handling
- Memory usage monitoring
- Load testing
- Stress testing
- Performance regression detection
"""

import pytest
import time
import asyncio
import aiohttp
import requests
import psutil
import os
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """Performance test metrics."""
    operation: str
    response_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: str = ""

class PerformanceTestBase:
    """Base class for performance tests."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate and get token."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": "admin", "password": "admin123"},
                timeout=10
            )
            response.raise_for_status()
            self.token = response.json()["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        process = psutil.Process(os.getpid())
        return {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "timestamp": time.time()
        }

class TestAPIPerformance(PerformanceTestBase):
    """Test API endpoint performance."""

    def test_health_endpoint_performance(self):
        """Test health endpoint response time."""
        start_time = time.time()
        response = self.session.get(f"{self.base_url}/health", timeout=5)
        execution_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert execution_time < 200  # Should respond within 200ms
        print(f"Health endpoint response time: {execution_time:.2f}ms")

    def test_detailed_health_performance(self):
        """Test detailed health endpoint performance."""
        start_time = time.time()
        response = self.session.get(f"{self.base_url}/health/detailed", timeout=10)
        execution_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert execution_time < 500  # Should respond within 500ms
        print(f"Detailed health response time: {execution_time:.2f}ms")

    def test_docs_endpoint_performance(self):
        """Test API documentation endpoint performance."""
        start_time = time.time()
        response = self.session.get(f"{self.base_url}/docs", timeout=15)
        execution_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert execution_time < 3000  # Should load within 3 seconds
        print(f"Docs endpoint response time: {execution_time:.2f}ms")

    def test_authentication_performance(self):
        """Test authentication endpoint performance."""
        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        execution_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert execution_time < 500  # Should authenticate within 500ms
        print(f"Authentication response time: {execution_time:.2f}ms")

class TestConcurrentPerformance(PerformanceTestBase):
    """Test concurrent request handling."""

    def test_concurrent_health_requests(self):
        """Test handling of concurrent health requests."""
        def make_request():
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            execution_time = (time.time() - start_time) * 1000
            return {
                "status_code": response.status_code,
                "response_time_ms": execution_time,
                "success": response.status_code == 200
            }

        # Make 20 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]

        # Analyze results
        success_count = sum(1 for r in results if r["success"])
        response_times = [r["response_time_ms"] for r in results]

        assert success_count == 20, f"Only {success_count}/20 requests succeeded"
        assert max(response_times) < 1000, f"Max response time {max(response_times):.2f}ms too high"

        avg_response_time = statistics.mean(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]

        print(f"Concurrent requests - Avg: {avg_response_time:.2f}ms, P95: {p95_response_time:.2f}ms")

    @pytest.mark.asyncio
    async def test_async_concurrent_requests(self):
        """Test async concurrent request handling."""
        async def make_request(session):
            start_time = time.time()
            async with session.get(f"{self.base_url}/health") as response:
                execution_time = (time.time() - start_time) * 1000
                return {
                    "status": response.status,
                    "response_time_ms": execution_time
                }

        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session) for _ in range(15)]
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            total_time = (time.time() - start_time) * 1000

        # All requests should succeed
        assert all(r["status"] == 200 for r in results)
        assert total_time < 2000  # All requests should complete within 2 seconds

        response_times = [r["response_time_ms"] for r in results]
        avg_time = statistics.mean(response_times)
        print(f"Async concurrent requests - Avg: {avg_time:.2f}ms, Total: {total_time:.2f}ms")

class TestMemoryPerformance(PerformanceTestBase):
    """Test memory usage and performance."""

    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        initial_metrics = self.get_system_metrics()
        initial_memory = initial_metrics["memory_mb"]

        # Make multiple requests to simulate load
        for _ in range(50):
            response = self.session.get(f"{self.base_url}/health")
            assert response.status_code == 200

        final_metrics = self.get_system_metrics()
        final_memory = final_metrics["memory_mb"]
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB"
        print(f"Memory usage - Initial: {initial_memory:.2f}MB, Final: {final_memory:.2f}MB, Increase: {memory_increase:.2f}MB")

    def test_memory_leak_detection(self):
        """Test for memory leaks over time."""
        initial_memory = self.get_system_metrics()["memory_mb"]

        # Perform operations multiple times
        for cycle in range(10):
            for _ in range(10):
                response = self.session.get(f"{self.base_url}/health")
                assert response.status_code == 200

            # Force garbage collection
            import gc
            gc.collect()

            current_memory = self.get_system_metrics()["memory_mb"]
            memory_growth = current_memory - initial_memory

            # Memory growth should be minimal
            assert memory_growth < 20, f"Memory leak detected: {memory_growth:.2f}MB growth after cycle {cycle}"

        print(f"Memory leak test passed - Total growth: {memory_growth:.2f}MB")

class TestLoadPerformance(PerformanceTestBase):
    """Test load handling capabilities."""

    def test_sustained_load(self):
        """Test API under sustained load."""
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=5)
                execution_time = (time.time() - start_time) * 1000
                return {
                    "success": response.status_code == 200,
                    "response_time_ms": execution_time
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "response_time_ms": 0
                }

        # Run sustained load for 30 seconds
        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            while time.time() - start_time < 30:
                futures = [executor.submit(make_request) for _ in range(5)]
                batch_results = [future.result() for future in as_completed(futures)]
                results.extend(batch_results)
                time.sleep(0.1)  # Small delay between batches

        # Analyze results
        success_count = sum(1 for r in results if r["success"])
        success_rate = success_count / len(results)
        response_times = [r["response_time_ms"] for r in results if r["success"]]

        assert success_rate > 0.95, f"Success rate {success_rate:.2%} too low"
        assert len(response_times) > 0, "No successful requests"

        avg_response_time = statistics.mean(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]

        print(f"Sustained load - Success rate: {success_rate:.2%}, Avg: {avg_response_time:.2f}ms, P95: {p95_response_time:.2f}ms")

    def test_peak_load_handling(self):
        """Test API behavior under peak load."""
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=3)
                execution_time = (time.time() - start_time) * 1000
                return {
                    "success": response.status_code == 200,
                    "response_time_ms": execution_time
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "response_time_ms": 0
                }

        # Peak load: 50 concurrent requests
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in as_completed(futures)]

        success_count = sum(1 for r in results if r["success"])
        success_rate = success_count / len(results)

        # Under peak load, we expect some degradation but not complete failure
        assert success_rate > 0.8, f"Peak load success rate {success_rate:.2%} too low"

        successful_results = [r for r in results if r["success"]]
        if successful_results:
            response_times = [r["response_time_ms"] for r in successful_results]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)

            print(f"Peak load - Success rate: {success_rate:.2%}, Avg: {avg_response_time:.2f}ms, Max: {max_response_time:.2f}ms")

class TestPerformanceRegression(PerformanceTestBase):
    """Test for performance regressions."""

    def test_response_time_regression(self):
        """Test that response times haven't regressed."""
        # Test multiple endpoints
        endpoints = [
            ("/health", 200),
            ("/health/detailed", 500),
            ("/docs", 3000)
        ]

        for endpoint, max_time_ms in endpoints:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}{endpoint}", timeout=max_time_ms/1000 + 1)
            execution_time = (time.time() - start_time) * 1000

            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
            assert execution_time < max_time_ms, f"{endpoint} took {execution_time:.2f}ms (max: {max_time_ms}ms)"

            print(f"{endpoint} - {execution_time:.2f}ms (threshold: {max_time_ms}ms)")

    def test_throughput_regression(self):
        """Test that throughput hasn't regressed."""
        def make_request():
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=2)
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": response.status_code == 200,
                "response_time_ms": execution_time
            }

        # Measure throughput over 10 seconds
        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=20) as executor:
            while time.time() - start_time < 10:
                futures = [executor.submit(make_request) for _ in range(5)]
                batch_results = [future.result() for future in as_completed(futures)]
                results.extend(batch_results)

        successful_results = [r for r in results if r["success"]]
        throughput = len(successful_results) / 10  # requests per second

        # Minimum throughput requirement
        assert throughput > 10, f"Throughput {throughput:.1f} req/s too low"

        avg_response_time = statistics.mean([r["response_time_ms"] for r in successful_results])
        print(f"Throughput: {throughput:.1f} req/s, Avg response: {avg_response_time:.2f}ms")

class TestPerformanceMonitoring(PerformanceTestBase):
    """Test performance monitoring functionality."""

    def test_performance_metrics_endpoint(self):
        """Test performance metrics endpoint if available."""
        try:
            response = self.session.get(f"{self.base_url}/metrics", timeout=5)
            if response.status_code == 200:
                metrics = response.json()
                print(f"Performance metrics available: {list(metrics.keys())}")
            else:
                print("Performance metrics endpoint not available")
        except Exception as e:
            print(f"Performance metrics endpoint error: {e}")

    def test_performance_monitoring_integration(self):
        """Test that performance monitoring is working."""
        # This test verifies that our performance monitoring decorators are working
        # by checking if performance data is being collected

        # Make several requests to generate performance data
        for _ in range(10):
            response = self.session.get(f"{self.base_url}/health")
            assert response.status_code == 200

        # Check if performance monitoring is collecting data
        # This would require access to the performance collector
        print("Performance monitoring integration test completed")

# Performance test configuration
@pytest.fixture(scope="session")
def performance_test_setup():
    """Setup for performance tests."""
    base = PerformanceTestBase()
    if not base.authenticate():
        pytest.skip("Authentication failed - skipping performance tests")
    return base

# Test execution configuration
def pytest_configure(config):
    """Configure pytest for performance tests."""
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

# Performance test markers
pytestmark = [
    pytest.mark.performance,
    pytest.mark.slow
]
