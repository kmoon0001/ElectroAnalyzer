"""Enterprise-grade Performance Monitoring System

Provides comprehensive performance monitoring with:
- Function-level timing
- Memory usage tracking
- Database query monitoring
- API endpoint performance
- Performance metrics collection
- Automatic performance alerts
"""

import time
import functools
import logging
import threading
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import contextmanager
import psutil
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation."""
    operation_name: str
    execution_time_ms: float
    memory_delta_mb: float
    cpu_usage_percent: float
    timestamp: datetime
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerformanceCollector:
    """Thread-safe performance metrics collector."""

    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_entries))
        self.lock = threading.RLock()
        self.thresholds = {
            'slow_operation_ms': 1000,  # 1 second
            'memory_warning_mb': 100,   # 100MB
            'cpu_warning_percent': 80   # 80%
        }

    def record_metrics(self, metrics: PerformanceMetrics) -> None:
        """Record performance metrics."""
        with self.lock:
            self.metrics[metrics.operation_name].append(metrics)

            # Check for performance warnings
            self._check_performance_warnings(metrics)

    def _check_performance_warnings(self, metrics: PerformanceMetrics) -> None:
        """Check for performance warnings and log them."""
        if metrics.execution_time_ms > self.thresholds['slow_operation_ms']:
            logger.warning(
                f"Slow operation detected: {metrics.operation_name} "
                f"took {metrics.execution_time_ms:.2f}ms"
            )

        if abs(metrics.memory_delta_mb) > self.thresholds['memory_warning_mb']:
            logger.warning(
                f"High memory usage: {metrics.operation_name} "
                f"used {metrics.memory_delta_mb:.2f}MB"
            )

        if metrics.cpu_usage_percent > self.thresholds['cpu_warning_percent']:
            logger.warning(
                f"High CPU usage: {metrics.operation_name} "
                f"used {metrics.cpu_usage_percent:.1f}% CPU"
            )

    def get_statistics(self, operation_name: str) -> Dict[str, Any]:
        """Get performance statistics for an operation."""
        with self.lock:
            if operation_name not in self.metrics or not self.metrics[operation_name]:
                return {'count': 0, 'message': 'No data available'}

            metrics_list = list(self.metrics[operation_name])
            execution_times = [m.execution_time_ms for m in metrics_list]
            memory_deltas = [m.memory_delta_mb for m in metrics_list]
            cpu_usage = [m.cpu_usage_percent for m in metrics_list]

            return {
                'count': len(metrics_list),
                'avg_execution_time_ms': sum(execution_times) / len(execution_times),
                'min_execution_time_ms': min(execution_times),
                'max_execution_time_ms': max(execution_times),
                'p95_execution_time_ms': sorted(execution_times)[int(len(execution_times) * 0.95)],
                'avg_memory_delta_mb': sum(memory_deltas) / len(memory_deltas),
                'max_memory_delta_mb': max(memory_deltas),
                'avg_cpu_usage_percent': sum(cpu_usage) / len(cpu_usage),
                'success_rate': sum(1 for m in metrics_list if m.success) / len(metrics_list),
                'last_execution': metrics_list[-1].timestamp.isoformat()
            }

    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        with self.lock:
            return {
                operation: self.get_statistics(operation)
                for operation in self.metrics.keys()
            }

    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest operations."""
        with self.lock:
            all_ops = []
            for operation_name in self.metrics.keys():
                stats = self.get_statistics(operation_name)
                if stats['count'] > 0:
                    all_ops.append({
                        'operation': operation_name,
                        'avg_time_ms': stats['avg_execution_time_ms'],
                        'max_time_ms': stats['max_execution_time_ms'],
                        'count': stats['count']
                    })

            return sorted(all_ops, key=lambda x: x['avg_time_ms'], reverse=True)[:limit]

# Global performance collector instance
performance_collector = PerformanceCollector()

def monitor_performance(
    operation_name: str,
    collect_memory: bool = True,
    collect_cpu: bool = True,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator to monitor function performance.

    Args:
        operation_name: Name of the operation being monitored
        collect_memory: Whether to track memory usage
        collect_cpu: Whether to track CPU usage
        metadata: Additional metadata to include
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            return _monitor_sync_function(
                func, operation_name, collect_memory, collect_cpu, metadata,
                args, kwargs
            )

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await _monitor_async_function(
                func, operation_name, collect_memory, collect_cpu, metadata,
                args, kwargs
            )

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def _monitor_sync_function(
    func: Callable,
    operation_name: str,
    collect_memory: bool,
    collect_cpu: bool,
    metadata: Optional[Dict[str, Any]],
    args: tuple,
    kwargs: dict
) -> Any:
    """Monitor synchronous function execution."""
    start_time = time.time()
    start_memory = _get_memory_usage() if collect_memory else 0
    start_cpu = _get_cpu_usage() if collect_cpu else 0

    success = True
    error_message = None

    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        success = False
        error_message = str(e)
        raise
    finally:
        end_time = time.time()
        end_memory = _get_memory_usage() if collect_memory else 0
        end_cpu = _get_cpu_usage() if collect_cpu else 0

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time_ms=(end_time - start_time) * 1000,
            memory_delta_mb=end_memory - start_memory,
            cpu_usage_percent=end_cpu - start_cpu,
            timestamp=datetime.now(timezone.utc),
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )

        performance_collector.record_metrics(metrics)

async def _monitor_async_function(
    func: Callable,
    operation_name: str,
    collect_memory: bool,
    collect_cpu: bool,
    metadata: Optional[Dict[str, Any]],
    args: tuple,
    kwargs: dict
) -> Any:
    """Monitor asynchronous function execution."""
    start_time = time.time()
    start_memory = _get_memory_usage() if collect_memory else 0
    start_cpu = _get_cpu_usage() if collect_cpu else 0

    success = True
    error_message = None

    try:
        result = await func(*args, **kwargs)
        return result
    except Exception as e:
        success = False
        error_message = str(e)
        raise
    finally:
        end_time = time.time()
        end_memory = _get_memory_usage() if collect_memory else 0
        end_cpu = _get_cpu_usage() if collect_cpu else 0

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time_ms=(end_time - start_time) * 1000,
            memory_delta_mb=end_memory - start_memory,
            cpu_usage_percent=end_cpu - start_cpu,
            timestamp=datetime.now(timezone.utc),
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )

        performance_collector.record_metrics(metrics)

def _get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except Exception:
        return 0.0

def _get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    try:
        process = psutil.Process(os.getpid())
        return process.cpu_percent()
    except Exception:
        return 0.0

@contextmanager
def monitor_operation(
    operation_name: str,
    collect_memory: bool = True,
    collect_cpu: bool = True,
    metadata: Optional[Dict[str, Any]] = None
):
    """Context manager for monitoring operations."""
    start_time = time.time()
    start_memory = _get_memory_usage() if collect_memory else 0
    start_cpu = _get_cpu_usage() if collect_cpu else 0

    success = True
    error_message = None

    try:
        yield
    except Exception as e:
        success = False
        error_message = str(e)
        raise
    finally:
        end_time = time.time()
        end_memory = _get_memory_usage() if collect_memory else 0
        end_cpu = _get_cpu_usage() if collect_cpu else 0

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time_ms=(end_time - start_time) * 1000,
            memory_delta_mb=end_memory - start_memory,
            cpu_usage_percent=end_cpu - start_cpu,
            timestamp=datetime.now(timezone.utc),
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )

        performance_collector.record_metrics(metrics)

class DatabaseQueryMonitor:
    """Monitor database query performance."""

    def __init__(self):
        self.query_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.RLock()

    def record_query(self, query: str, execution_time_ms: float, success: bool = True) -> None:
        """Record database query performance."""
        with self.lock:
            # Normalize query for grouping (remove specific values)
            normalized_query = self._normalize_query(query)

            self.query_metrics[normalized_query].append({
                'execution_time_ms': execution_time_ms,
                'success': success,
                'timestamp': datetime.now(timezone.utc),
                'original_query': query[:100]  # Store first 100 chars for debugging
            })

    def _normalize_query(self, query: str) -> str:
        """Normalize query by removing specific values."""
        import re
        # Replace quoted strings and numbers with placeholders
        normalized = re.sub(r"'[^']*'", "'?'", query)
        normalized = re.sub(r'\b\d+\b', '?', normalized)
        return normalized.strip()

    def get_slow_queries(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        """Get queries that exceed the threshold."""
        with self.lock:
            slow_queries = []
            for query, metrics in self.query_metrics.items():
                if metrics:
                    avg_time = sum(m['execution_time_ms'] for m in metrics) / len(metrics)
                    if avg_time > threshold_ms:
                        slow_queries.append({
                            'query': query,
                            'avg_time_ms': avg_time,
                            'max_time_ms': max(m['execution_time_ms'] for m in metrics),
                            'count': len(metrics),
                            'success_rate': sum(1 for m in metrics if m['success']) / len(metrics)
                        })

            return sorted(slow_queries, key=lambda x: x['avg_time_ms'], reverse=True)

# Global database monitor instance
db_monitor = DatabaseQueryMonitor()

def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    return {
        'overall_statistics': performance_collector.get_all_statistics(),
        'slowest_operations': performance_collector.get_slowest_operations(),
        'slow_queries': db_monitor.get_slow_queries(),
        'system_info': {
            'memory_usage_mb': _get_memory_usage(),
            'cpu_usage_percent': _get_cpu_usage(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    }

# Import asyncio for async function detection
import asyncio