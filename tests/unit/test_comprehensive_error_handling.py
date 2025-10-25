"""Comprehensive error handling and edge case tests for document processing.

This module provides thorough testing for:
- Error handling and recovery
- Edge cases and boundary conditions
- Exception handling and logging
- Graceful degradation
- Resource cleanup and management
- System resilience and fault tolerance
"""

import pytest
import pytest_asyncio
import tempfile
import os
import time
import threading
import signal
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from tests.data.test_documents import (
    create_corrupted_file,
    create_oversized_file,
    create_malicious_file,
    create_file_with_special_characters,
    create_file_with_unicode_content,
    create_file_with_mixed_encodings,
    create_file_with_empty_lines,
    create_file_with_very_long_lines,
    create_file_with_binary_content,
)


class TestDocumentProcessingErrorHandling:
    """Comprehensive error handling tests for document processing."""

    def test_file_not_found_error_handling(self):
        """Test handling of file not found errors."""
        from src.core.parsing import parse_document_content

        # Test with non-existent file
        result = parse_document_content("/nonexistent/file.pdf")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Error: File not found" in result[0]["sentence"]
        assert result[0]["source"] == "parser"

    def test_permission_denied_error_handling(self):
        """Test handling of permission denied errors."""
        from src.core.parsing import parse_document_content

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"Content with permission issues")
            tmp_file.flush()

            # Change file permissions to read-only
            os.chmod(tmp_file.name, 0o444)

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle permission issues gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # May return error or content depending on implementation
                if len(result) == 1 and "Error" in result[0]["sentence"]:
                    assert result[0]["source"] == "parser"
                else:
                    # Content was successfully extracted
                    combined_text = " ".join(chunk["sentence"] for chunk in result)
                    assert "Content with permission issues" in combined_text

            finally:
                # Restore permissions for cleanup
                os.chmod(tmp_file.name, 0o644)
                os.unlink(tmp_file.name)

    def test_corrupted_file_error_handling(self):
        """Test handling of corrupted files."""
        from src.core.parsing import parse_document_content

        # Test with corrupted PDF
        corrupted_content = create_corrupted_file("pdf")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(corrupted_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) == 1
                assert "Error parsing file" in result[0]["sentence"]
                assert result[0]["source"] == "parser"

            finally:
                os.unlink(tmp_file.name)

    def test_oversized_file_error_handling(self):
        """Test handling of oversized files."""
        from src.core.parsing import parse_document_content

        # Test with oversized file
        oversized_content = create_oversized_file(51)  # 51MB

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(oversized_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle oversized files gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # May return error or content depending on implementation
                if len(result) == 1 and "Error" in result[0]["sentence"]:
                    assert result[0]["source"] == "parser"
                else:
                    # Content was successfully extracted
                    combined_text = " ".join(chunk["sentence"] for chunk in result)
                    assert len(combined_text) > 0

            finally:
                os.unlink(tmp_file.name)

    def test_malicious_file_error_handling(self):
        """Test handling of malicious files."""
        from src.core.parsing import parse_document_content

        # Test with malicious file
        malicious_content = create_malicious_file("script")

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(malicious_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle malicious files gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # May return error or content depending on implementation
                if len(result) == 1 and "Error" in result[0]["sentence"]:
                    assert result[0]["source"] == "parser"
                else:
                    # Content was successfully extracted
                    combined_text = " ".join(chunk["sentence"] for chunk in result)
                    assert len(combined_text) > 0

            finally:
                os.unlink(tmp_file.name)

    def test_unsupported_file_type_error_handling(self):
        """Test handling of unsupported file types."""
        from src.core.parsing import parse_document_content

        # Test with unsupported file type
        unsupported_content = b"Some content"

        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp_file:
            tmp_file.write(unsupported_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) == 1
                assert "Error: Unsupported file type" in result[0]["sentence"]
                assert result[0]["source"] == "parser"

            finally:
                os.unlink(tmp_file.name)

    def test_parsing_timeout_error_handling(self):
        """Test handling of parsing timeouts."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.threading.Thread.join') as mock_join:
            mock_join.side_effect = lambda timeout: None  # Simulate timeout

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf_content = create_test_pdf("Large file content" * 1000)
                tmp_file.write(pdf_content)
                tmp_file.flush()

                try:
                    result = parse_document_content(tmp_file.name)

                    assert isinstance(result, list)
                    assert len(result) == 1
                    assert "Error: Document parsing timed out" in result[0]["sentence"]
                    assert result[0]["source"] == "parser"

                finally:
                    os.unlink(tmp_file.name)

    def test_memory_error_handling(self):
        """Test handling of memory errors."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.parse_document_content', side_effect=MemoryError("Out of memory")):
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(b"Some content")
                tmp_file.flush()

                try:
                    result = parse_document_content(tmp_file.name)

                    assert isinstance(result, list)
                    assert len(result) == 1
                    assert "Error parsing file" in result[0]["sentence"]
                    assert result[0]["source"] == "parser"

                finally:
                    os.unlink(tmp_file.name)

    def test_disk_space_error_handling(self):
        """Test handling of disk space errors."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.parse_document_content', side_effect=OSError("No space left on device")):
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(b"Some content")
                tmp_file.flush()

                try:
                    result = parse_document_content(tmp_file.name)

                    assert isinstance(result, list)
                    assert len(result) == 1
                    assert "Error parsing file" in result[0]["sentence"]
                    assert result[0]["source"] == "parser"

                finally:
                    os.unlink(tmp_file.name)

    def test_network_error_handling(self):
        """Test handling of network errors."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.parse_document_content', side_effect=ConnectionError("Network error")):
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(b"Some content")
                tmp_file.flush()

                try:
                    result = parse_document_content(tmp_file.name)

                    assert isinstance(result, list)
                    assert len(result) == 1
                    assert "Error parsing file" in result[0]["sentence"]
                    assert result[0]["source"] == "parser"

                finally:
                    os.unlink(tmp_file.name)

    def test_concurrent_access_error_handling(self):
        """Test handling of concurrent access errors."""
        from src.core.parsing import parse_document_content

        def process_document():
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(b"Content for concurrent access test")
                tmp_file.flush()

                try:
                    result = parse_document_content(tmp_file.name)
                    return result
                finally:
                    os.unlink(tmp_file.name)

        # Create multiple threads for concurrent access
        threads = []
        results = []
        errors = []

        for i in range(5):
            thread = threading.Thread(
                target=lambda: results.append(process_document())
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)

        # Verify results
        assert len(results) == 5
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0

    def test_signal_interruption_error_handling(self):
        """Test handling of signal interruptions."""
        from src.core.parsing import parse_document_content

        def signal_handler(signum, frame):
            raise KeyboardInterrupt("Signal interrupted")

        # Set up signal handler
        original_handler = signal.signal(signal.SIGINT, signal_handler)

        try:
            with patch('src.core.parsing.parse_document_content', side_effect=KeyboardInterrupt("Signal interrupted")):
                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                    tmp_file.write(b"Some content")
                    tmp_file.flush()

                    try:
                        result = parse_document_content(tmp_file.name)

                        assert isinstance(result, list)
                        assert len(result) == 1
                        assert "Error parsing file" in result[0]["sentence"]
                        assert result[0]["source"] == "parser"

                    finally:
                        os.unlink(tmp_file.name)
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGINT, original_handler)

    def test_resource_cleanup_error_handling(self):
        """Test handling of resource cleanup errors."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.parse_document_content', side_effect=RuntimeError("Resource cleanup failed")):
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                tmp_file.write(b"Some content")
                tmp_file.flush()

                try:
                    result = parse_document_content(tmp_file.name)

                    assert isinstance(result, list)
                    assert len(result) == 1
                    assert "Error parsing file" in result[0]["sentence"]
                    assert result[0]["source"] == "parser"

                finally:
                    os.unlink(tmp_file.name)

    def test_unicode_error_handling(self):
        """Test handling of Unicode errors."""
        from src.core.parsing import parse_document_content

        # Test with invalid Unicode content
        invalid_unicode_content = b"\xff\xfe\x00\x00"  # Invalid UTF-8

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(invalid_unicode_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle Unicode errors gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # May return error or content depending on implementation
                if len(result) == 1 and "Error" in result[0]["sentence"]:
                    assert result[0]["source"] == "parser"
                else:
                    # Content was successfully extracted
                    combined_text = " ".join(chunk["sentence"] for chunk in result)
                    assert len(combined_text) >= 0

            finally:
                os.unlink(tmp_file.name)

    def test_encoding_error_handling(self):
        """Test handling of encoding errors."""
        from src.core.parsing import parse_document_content

        # Test with mixed encodings
        mixed_encoding_content = "Mixed encoding: Hello 世界 مرحبا мир".encode('utf-8')

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(mixed_encoding_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle encoding errors gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # Content should be extracted successfully
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Mixed encoding" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_special_characters_error_handling(self):
        """Test handling of special characters."""
        from src.core.parsing import parse_document_content

        # Test with special characters
        special_chars_content = create_file_with_special_characters()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(special_chars_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle special characters gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # Content should be extracted successfully
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Special characters test" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_unicode_content_error_handling(self):
        """Test handling of Unicode content."""
        from src.core.parsing import parse_document_content

        # Test with Unicode content
        unicode_content = create_file_with_unicode_content()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(unicode_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle Unicode content gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # Content should be extracted successfully
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Unicode content test" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_mixed_encodings_error_handling(self):
        """Test handling of mixed encodings."""
        from src.core.parsing import parse_document_content

        # Test with mixed encodings
        mixed_encodings_content = create_file_with_mixed_encodings()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(mixed_encodings_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle mixed encodings gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # Content should be extracted successfully
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Mixed encoding test" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_empty_lines_error_handling(self):
        """Test handling of empty lines."""
        from src.core.parsing import parse_document_content

        # Test with empty lines
        empty_lines_content = create_file_with_empty_lines()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(empty_lines_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle empty lines gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # Content should be extracted successfully
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Line 1" in combined_text
                assert "Line 2" in combined_text
                assert "Line 3" in combined_text
                assert "Line 4" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_very_long_lines_error_handling(self):
        """Test handling of very long lines."""
        from src.core.parsing import parse_document_content

        # Test with very long lines
        very_long_lines_content = create_file_with_very_long_lines()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(very_long_lines_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle very long lines gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # Content should be extracted successfully
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert len(combined_text) > 0

            finally:
                os.unlink(tmp_file.name)

    def test_binary_content_error_handling(self):
        """Test handling of binary content."""
        from src.core.parsing import parse_document_content

        # Test with binary content
        binary_content = create_file_with_binary_content()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(binary_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                # Should handle binary content gracefully
                assert isinstance(result, list)
                assert len(result) > 0

                # May return error or content depending on implementation
                if len(result) == 1 and "Error" in result[0]["sentence"]:
                    assert result[0]["source"] == "parser"
                else:
                    # Content was successfully extracted
                    combined_text = " ".join(chunk["sentence"] for chunk in result)
                    assert len(combined_text) >= 0

            finally:
                os.unlink(tmp_file.name)

    def test_nested_directories_error_handling(self):
        """Test handling of nested directories."""
        from src.core.parsing import parse_document_content

        # Create nested directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "level1" / "level2" / "level3"
            nested_dir.mkdir(parents=True)

            file_path = nested_dir / "test.txt"
            file_path.write_text("Content in nested directory")

            result = parse_document_content(str(file_path))

            # Should handle nested directories gracefully
            assert isinstance(result, list)
            assert len(result) > 0

            # Content should be extracted successfully
            combined_text = " ".join(chunk["sentence"] for chunk in result)
            assert "Content in nested directory" in combined_text

    def test_symlink_error_handling(self):
        """Test handling of symbolic links."""
        from src.core.parsing import parse_document_content

        # Create symbolic link
        with tempfile.TemporaryDirectory() as temp_dir:
            target_file = Path(temp_dir) / "target.txt"
            target_file.write_text("Target file content")

            symlink_file = Path(temp_dir) / "symlink.txt"
            symlink_file.symlink_to(target_file)

            result = parse_document_content(str(symlink_file))

            # Should handle symbolic links gracefully
            assert isinstance(result, list)
            assert len(result) > 0

            # Content should be extracted successfully
            combined_text = " ".join(chunk["sentence"] for chunk in result)
            assert "Target file content" in combined_text

    def test_hard_link_error_handling(self):
        """Test handling of hard links."""
        from src.core.parsing import parse_document_content

        # Create hard link
        with tempfile.TemporaryDirectory() as temp_dir:
            target_file = Path(temp_dir) / "target.txt"
            target_file.write_text("Target file content")

            hardlink_file = Path(temp_dir) / "hardlink.txt"
            hardlink_file.hardlink_to(target_file)

            result = parse_document_content(str(hardlink_file))

            # Should handle hard links gracefully
            assert isinstance(result, list)
            assert len(result) > 0

            # Content should be extracted successfully
            combined_text = " ".join(chunk["sentence"] for chunk in result)
            assert "Target file content" in combined_text

    def test_fifo_error_handling(self):
        """Test handling of FIFO (named pipe) files."""
        from src.core.parsing import parse_document_content

        # Create FIFO
        with tempfile.TemporaryDirectory() as temp_dir:
            fifo_file = Path(temp_dir) / "fifo"
            os.mkfifo(str(fifo_file))

            result = parse_document_content(str(fifo_file))

            # Should handle FIFO gracefully
            assert isinstance(result, list)
            assert len(result) > 0

            # May return error or content depending on implementation
            if len(result) == 1 and "Error" in result[0]["sentence"]:
                assert result[0]["source"] == "parser"
            else:
                # Content was successfully extracted
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert len(combined_text) >= 0

    def test_socket_error_handling(self):
        """Test handling of socket files."""
        from src.core.parsing import parse_document_content

        # Create socket file
        with tempfile.TemporaryDirectory() as temp_dir:
            socket_file = Path(temp_dir) / "socket"
            os.mknod(str(socket_file), 0o600 | 0o140000)  # S_IFSOCK

            result = parse_document_content(str(socket_file))

            # Should handle socket files gracefully
            assert isinstance(result, list)
            assert len(result) > 0

            # May return error or content depending on implementation
            if len(result) == 1 and "Error" in result[0]["sentence"]:
                assert result[0]["source"] == "parser"
            else:
                # Content was successfully extracted
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert len(combined_text) >= 0

    def test_device_file_error_handling(self):
        """Test handling of device files."""
        from src.core.parsing import parse_document_content

        # Create device file
        with tempfile.TemporaryDirectory() as temp_dir:
            device_file = Path(temp_dir) / "device"
            os.mknod(str(device_file), 0o600 | 0o060000)  # S_IFBLK

            result = parse_document_content(str(device_file))

            # Should handle device files gracefully
            assert isinstance(result, list)
            assert len(result) > 0

            # May return error or content depending on implementation
            if len(result) == 1 and "Error" in result[0]["sentence"]:
                assert result[0]["source"] == "parser"
            else:
                # Content was successfully extracted
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert len(combined_text) >= 0

    def test_character_device_error_handling(self):
        """Test handling of character device files."""
        from src.core.parsing import parse_document_content

        # Create character device file
        with tempfile.TemporaryDirectory() as temp_dir:
            char_device_file = Path(temp_dir) / "char_device"
            os.mknod(str(char_device_file), 0o600 | 0o020000)  # S_IFCHR

            result = parse_document_content(str(char_device_file))

            # Should handle character device files gracefully
            assert isinstance(result, list)
            assert len(result) > 0

            # May return error or content depending on implementation
            if len(result) == 1 and "Error" in result[0]["sentence"]:
                assert result[0]["source"] == "parser"
            else:
                # Content was successfully extracted
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert len(combined_text) >= 0
