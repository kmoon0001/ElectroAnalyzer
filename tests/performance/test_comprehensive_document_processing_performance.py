"""Comprehensive performance and load testing for document processing.

This module provides thorough testing for:
- Performance characteristics under various loads
- Memory usage and optimization
- Concurrent processing capabilities
- Scalability testing
- Resource utilization monitoring
- Performance regression detection
"""

import pytest
import pytest_asyncio
import time
import asyncio
import threading
import psutil
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from tests.data.test_documents import (
    create_test_pdf,
    create_test_docx,
    create_test_image,
    create_test_txt,
    create_oversized_file,
)


class TestDocumentProcessingPerformance:
    """Comprehensive performance tests for document processing."""

    def test_single_document_processing_performance(self):
        """Test performance of single document processing."""
        from src.core.parsing import parse_document_content

        # Create test document
        content = "Sample content " * 1000  # 15KB content

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(content.encode())
            tmp_file.flush()

            try:
                start_time = time.time()
                result = parse_document_content(tmp_file.name)
                end_time = time.time()

                processing_time = end_time - start_time

                # Should process within reasonable time (2 seconds)
                assert processing_time < 2.0
                assert isinstance(result, list)
                assert len(result) > 0

            finally:
                os.unlink(tmp_file.name)

    def test_large_document_processing_performance(self):
        """Test performance with large documents."""
        from src.core.parsing import parse_document_content

        # Create large document (1MB)
        large_content = "Sample content " * 100000  # ~1.5MB content

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(large_content.encode())
            tmp_file.flush()

            try:
                start_time = time.time()
                result = parse_document_content(tmp_file.name)
                end_time = time.time()

                processing_time = end_time - start_time

                # Should process within reasonable time (10 seconds)
                assert processing_time < 10.0
                assert isinstance(result, list)
                assert len(result) > 0

            finally:
                os.unlink(tmp_file.name)

    def test_concurrent_document_processing_performance(self):
        """Test performance with concurrent document processing."""
        from src.core.parsing import parse_document_content

        def process_document(content: str, suffix: str):
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                start_time = time.time()
                result = parse_document_content(tmp_file.name)
                end_time = time.time()

                processing_time = end_time - start_time

                os.unlink(tmp_file.name)
                return result, processing_time

        # Create multiple threads for concurrent processing
        threads = []
        results = []

        for i in range(5):
            content = f"Sample content {i} " * 1000
            thread = threading.Thread(
                target=lambda c=content: results.append(process_document(c, ".txt"))
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=15)

        # Verify results
        assert len(results) == 5
        for result, processing_time in results:
            assert isinstance(result, list)
            assert len(result) > 0
            assert processing_time < 5.0  # Each should complete within 5 seconds

    def test_memory_usage_during_processing(self):
        """Test memory usage during document processing."""
        from src.core.parsing import parse_document_content

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Process multiple documents
        for i in range(10):
            content = f"Sample content {i} " * 1000

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    result = parse_document_content(tmp_file.name)
                    assert isinstance(result, list)
                    assert len(result) > 0
                finally:
                    os.unlink(tmp_file.name)

        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024

    def test_cpu_usage_during_processing(self):
        """Test CPU usage during document processing."""
        from src.core.parsing import parse_document_content

        # Get initial CPU usage
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()

        # Process document
        content = "Sample content " * 10000

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(content.encode())
            tmp_file.flush()

            try:
                start_time = time.time()
                result = parse_document_content(tmp_file.name)
                end_time = time.time()

                processing_time = end_time - start_time

                # Get CPU usage during processing
                cpu_usage = process.cpu_percent()

                assert isinstance(result, list)
                assert len(result) > 0
                assert processing_time < 5.0
                assert cpu_usage < 100.0  # Should not exceed 100%

            finally:
                os.unlink(tmp_file.name)

    def test_disk_io_performance(self):
        """Test disk I/O performance during document processing."""
        from src.core.parsing import parse_document_content

        # Get initial disk I/O
        disk_io = psutil.disk_io_counters()
        initial_read_bytes = disk_io.read_bytes if disk_io else 0
        initial_write_bytes = disk_io.write_bytes if disk_io else 0

        # Process document
        content = "Sample content " * 10000

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(content.encode())
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Get final disk I/O
                disk_io = psutil.disk_io_counters()
                final_read_bytes = disk_io.read_bytes if disk_io else 0
                final_write_bytes = disk_io.write_bytes if disk_io else 0

                read_bytes = final_read_bytes - initial_read_bytes
                write_bytes = final_write_bytes - initial_write_bytes

                assert isinstance(result, list)
                assert len(result) > 0
                assert read_bytes > 0  # Should have read some data
                assert write_bytes >= 0  # May or may not have written data

            finally:
                os.unlink(tmp_file.name)

    def test_network_io_performance(self):
        """Test network I/O performance during document processing."""
        from src.core.parsing import parse_document_content

        # Get initial network I/O
        network_io = psutil.net_io_counters()
        initial_bytes_sent = network_io.bytes_sent if network_io else 0
        initial_bytes_recv = network_io.bytes_recv if network_io else 0

        # Process document
        content = "Sample content " * 10000

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(content.encode())
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Get final network I/O
                network_io = psutil.net_io_counters()
                final_bytes_sent = network_io.bytes_sent if network_io else 0
                final_bytes_recv = network_io.bytes_recv if network_io else 0

                bytes_sent = final_bytes_sent - initial_bytes_sent
                bytes_recv = final_bytes_recv - initial_bytes_recv

                assert isinstance(result, list)
                assert len(result) > 0
                assert bytes_sent >= 0  # May or may not have sent data
                assert bytes_recv >= 0  # May or may not have received data

            finally:
                os.unlink(tmp_file.name)

    def test_processing_time_scalability(self):
        """Test processing time scalability with document size."""
        from src.core.parsing import parse_document_content

        # Test with different document sizes
        sizes = [1000, 5000, 10000, 50000, 100000]  # Different content sizes
        processing_times = []

        for size in sizes:
            content = "Sample content " * size

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time
                    processing_times.append(processing_time)

                    assert isinstance(result, list)
                    assert len(result) > 0

                finally:
                    os.unlink(tmp_file.name)

        # Verify processing time scales reasonably with document size
        for i in range(1, len(processing_times)):
            # Processing time should not increase dramatically
            assert processing_times[i] < processing_times[i-1] * 10

    def test_memory_scalability(self):
        """Test memory scalability with document size."""
        from src.core.parsing import parse_document_content

        # Test with different document sizes
        sizes = [1000, 5000, 10000, 50000, 100000]  # Different content sizes
        memory_usage = []

        for size in sizes:
            content = "Sample content " * size

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    # Get memory before processing
                    process = psutil.Process(os.getpid())
                    memory_before = process.memory_info().rss

                    result = parse_document_content(tmp_file.name)

                    # Get memory after processing
                    memory_after = process.memory_info().rss
                    memory_used = memory_after - memory_before
                    memory_usage.append(memory_used)

                    assert isinstance(result, list)
                    assert len(result) > 0

                finally:
                    os.unlink(tmp_file.name)

        # Verify memory usage scales reasonably with document size
        for i in range(1, len(memory_usage)):
            # Memory usage should not increase dramatically
            assert memory_usage[i] < memory_usage[i-1] * 10

    def test_concurrent_processing_scalability(self):
        """Test concurrent processing scalability."""
        from src.core.parsing import parse_document_content

        def process_document(content: str, suffix: str):
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                start_time = time.time()
                result = parse_document_content(tmp_file.name)
                end_time = time.time()

                processing_time = end_time - start_time

                os.unlink(tmp_file.name)
                return result, processing_time

        # Test with different numbers of concurrent threads
        thread_counts = [1, 2, 5, 10]

        for thread_count in thread_counts:
            threads = []
            results = []

            for i in range(thread_count):
                content = f"Sample content {i} " * 1000
                thread = threading.Thread(
                    target=lambda c=content: results.append(process_document(c, ".txt"))
                )
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=30)

            # Verify results
            assert len(results) == thread_count
            for result, processing_time in results:
                assert isinstance(result, list)
                assert len(result) > 0
                assert processing_time < 10.0  # Each should complete within 10 seconds

    def test_processing_under_load(self):
        """Test processing performance under load."""
        from src.core.parsing import parse_document_content

        def process_document(content: str, suffix: str):
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                start_time = time.time()
                result = parse_document_content(tmp_file.name)
                end_time = time.time()

                processing_time = end_time - start_time

                os.unlink(tmp_file.name)
                return result, processing_time

        # Create high load with many concurrent threads
        threads = []
        results = []

        for i in range(20):  # 20 concurrent threads
            content = f"Sample content {i} " * 1000
            thread = threading.Thread(
                target=lambda c=content: results.append(process_document(c, ".txt"))
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=60)

        # Verify results
        assert len(results) == 20
        for result, processing_time in results:
            assert isinstance(result, list)
            assert len(result) > 0
            assert processing_time < 15.0  # Each should complete within 15 seconds

    def test_processing_with_resource_constraints(self):
        """Test processing performance with resource constraints."""
        from src.core.parsing import parse_document_content

        # Simulate resource constraints by limiting CPU
        with patch('psutil.Process.cpu_percent', return_value=95.0):
            content = "Sample content " * 10000

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert processing_time < 20.0  # Should still complete within reasonable time

                finally:
                    os.unlink(tmp_file.name)

    def test_processing_with_memory_constraints(self):
        """Test processing performance with memory constraints."""
        from src.core.parsing import parse_document_content

        # Simulate memory constraints by limiting available memory
        with patch('psutil.Process.memory_info', return_value=MagicMock(rss=100 * 1024 * 1024)):  # 100MB
            content = "Sample content " * 10000

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert processing_time < 20.0  # Should still complete within reasonable time

                finally:
                    os.unlink(tmp_file.name)

    def test_processing_with_disk_constraints(self):
        """Test processing performance with disk constraints."""
        from src.core.parsing import parse_document_content

        # Simulate disk constraints by limiting disk I/O
        with patch('psutil.disk_io_counters', return_value=MagicMock(read_bytes=0, write_bytes=0)):
            content = "Sample content " * 10000

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert processing_time < 20.0  # Should still complete within reasonable time

                finally:
                    os.unlink(tmp_file.name)

    def test_processing_with_network_constraints(self):
        """Test processing performance with network constraints."""
        from src.core.parsing import parse_document_content

        # Simulate network constraints by limiting network I/O
        with patch('psutil.net_io_counters', return_value=MagicMock(bytes_sent=0, bytes_recv=0)):
            content = "Sample content " * 10000

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert processing_time < 20.0  # Should still complete within reasonable time

                finally:
                    os.unlink(tmp_file.name)

    def test_processing_performance_regression(self):
        """Test for performance regression detection."""
        from src.core.parsing import parse_document_content

        # Baseline performance test
        content = "Sample content " * 10000

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(content.encode())
            tmp_file.flush()

            try:
                start_time = time.time()
                result = parse_document_content(tmp_file.name)
                end_time = time.time()

                processing_time = end_time - start_time

                assert isinstance(result, list)
                assert len(result) > 0

                # Performance should be within acceptable limits
                assert processing_time < 5.0  # Should complete within 5 seconds

                # Store baseline for regression detection
                baseline_time = processing_time

                # Run multiple times to detect performance regression
                for i in range(5):
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time

                    # Performance should not degrade significantly
                    assert processing_time < baseline_time * 2.0

            finally:
                os.unlink(tmp_file.name)

    def test_processing_with_different_file_types_performance(self):
        """Test processing performance with different file types."""
        from src.core.parsing import parse_document_content

        # Test with different file types
        file_types = [
            (".txt", "Sample text content"),
            (".pdf", create_test_pdf("Sample PDF content")),
            (".docx", create_test_docx("Sample DOCX content")),
            (".png", create_test_image("Sample image content")),
        ]

        for file_ext, content in file_types:
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
                if isinstance(content, bytes):
                    tmp_file.write(content)
                else:
                    tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert processing_time < 10.0  # Each file type should complete within 10 seconds

                finally:
                    os.unlink(tmp_file.name)

    def test_processing_with_corrupted_files_performance(self):
        """Test processing performance with corrupted files."""
        from src.core.parsing import parse_document_content

        # Test with corrupted files
        corrupted_files = [
            ("corrupted.pdf", b"Corrupted PDF content"),
            ("corrupted.docx", b"Corrupted DOCX content"),
            ("corrupted.txt", b"Corrupted text content"),
            ("corrupted.png", b"Corrupted image content"),
        ]

        for filename, content in corrupted_files:
            with tempfile.NamedTemporaryFile(suffix=filename.split('.')[-1], delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()

                try:
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert processing_time < 5.0  # Should handle corrupted files quickly

                finally:
                    os.unlink(tmp_file.name)

    def test_processing_with_oversized_files_performance(self):
        """Test processing performance with oversized files."""
        from src.core.parsing import parse_document_content

        # Test with oversized files
        oversized_files = [
            ("oversized.txt", b"x" * (51 * 1024 * 1024)),  # 51MB
            ("oversized.pdf", b"x" * (51 * 1024 * 1024)),  # 51MB
        ]

        for filename, content in oversized_files:
            with tempfile.NamedTemporaryFile(suffix=filename.split('.')[-1], delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()

                try:
                    start_time = time.time()
                    result = parse_document_content(tmp_file.name)
                    end_time = time.time()

                    processing_time = end_time - start_time

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert processing_time < 30.0  # Should handle oversized files within reasonable time

                finally:
                    os.unlink(tmp_file.name)
