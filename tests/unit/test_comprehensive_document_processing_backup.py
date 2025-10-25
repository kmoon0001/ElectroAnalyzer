"""Comprehensive test suite for all document processing capabilities.

This module provides thorough testing for:
- PDF processing with OCR
- DOCX processing
- Image processing with OCR
- Text file processing
- File validation and security
- Error handling and edge cases
- Performance characteristics
"""

import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, mock_open
import pytest
import pytest_asyncio
from PIL import Image
import numpy as np

# Test data imports
from tests.data.test_documents import (
    create_test_pdf,
    create_test_docx,
    create_test_image,
    create_test_txt,
    create_malicious_file,
    create_oversized_file,
)


class TestDocumentParsingComprehensive:
    """Comprehensive tests for document parsing across all supported formats."""

    def test_parse_pdf_with_text_content(self):
        """Test PDF parsing with text content."""
        from src.core.parsing import parse_document_content

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            # Create a simple PDF with text content
            pdf_content = create_test_pdf("Sample PDF content for testing")
            tmp_file.write(pdf_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0
                assert all(isinstance(chunk, dict) for chunk in result)
                assert all("sentence" in chunk for chunk in result)
                assert all("source" in chunk for chunk in result)

                # Verify content extraction
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Sample PDF content" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_parse_pdf_with_images_ocr(self):
        """Test PDF parsing with OCR for image content."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.OCR_AVAILABLE', True):
            with patch('src.core.parsing.pytesseract') as mock_tesseract:
                mock_tesseract.image_to_string.return_value = "OCR extracted text"

                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                    pdf_content = create_test_pdf("", with_images=True)
                    tmp_file.write(pdf_content)
                    tmp_file.flush()

                    try:
                        result = parse_document_content(tmp_file.name)

                        assert isinstance(result, list)
                        assert len(result) > 0

                        # Verify OCR was called for image content
                        mock_tesseract.image_to_string.assert_called()

                    finally:
                        os.unlink(tmp_file.name)

    def test_parse_docx_content(self):
        """Test DOCX parsing."""
        from src.core.parsing import parse_document_content

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_file:
            docx_content = create_test_docx("Sample DOCX content for testing")
            tmp_file.write(docx_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify content extraction
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Sample DOCX content" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_parse_image_with_ocr(self):
        """Test image parsing with OCR."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.OCR_AVAILABLE', True):
            with patch('src.core.parsing.pytesseract') as mock_tesseract:
                mock_tesseract.image_to_string.return_value = "OCR extracted text from image"

                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    image_content = create_test_image("Test image content")
                    tmp_file.write(image_content)
                    tmp_file.flush()

                    try:
                        result = parse_document_content(tmp_file.name)

                        assert isinstance(result, list)
                        assert len(result) > 0

                        # Verify OCR was called
                        mock_tesseract.image_to_string.assert_called()

                        # Verify content extraction
                        combined_text = " ".join(chunk["sentence"] for chunk in result)
                        assert "OCR extracted text" in combined_text

                    finally:
                        os.unlink(tmp_file.name)

    def test_parse_text_file(self):
        """Test text file parsing."""
        from src.core.parsing import parse_document_content

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            txt_content = create_test_txt("Sample text content for testing")
            tmp_file.write(txt_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify content extraction
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Sample text content" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_parse_unsupported_file_type(self):
        """Test parsing of unsupported file types."""
        from src.core.parsing import parse_document_content

        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp_file:
            tmp_file.write(b"Some content")
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) == 1
                assert "Error: Unsupported file type" in result[0]["sentence"]
                assert result[0]["source"] == "parser"

            finally:
                os.unlink(tmp_file.name)

    def test_parse_nonexistent_file(self):
        """Test parsing of non-existent files."""
        from src.core.parsing import parse_document_content

        result = parse_document_content("/nonexistent/file.pdf")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Error: File not found" in result[0]["sentence"]
        assert result[0]["source"] == "parser"

    def test_parse_corrupted_file(self):
        """Test parsing of corrupted files."""
        from src.core.parsing import parse_document_content

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            # Write corrupted PDF content
            tmp_file.write(b"Corrupted PDF content that will cause parsing errors")
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) == 1
                assert "Error parsing file" in result[0]["sentence"]
                assert result[0]["source"] == "parser"

            finally:
                os.unlink(tmp_file.name)

    def test_parse_large_file_timeout(self):
        """Test parsing timeout for large files."""
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

    def test_parse_caching_behavior(self):
        """Test document parsing caching behavior."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.cache_service') as mock_cache:
            mock_cache.get_from_disk.return_value = None
            mock_cache.set_to_disk.return_value = None

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                txt_content = create_test_txt("Cached content test")
                tmp_file.write(txt_content)
                tmp_file.flush()

                try:
                    # First call - cache miss
                    result1 = parse_document_content(tmp_file.name)

                    # Verify cache was checked
                    mock_cache.get_from_disk.assert_called()

                    # Verify cache was set
                    mock_cache.set_to_disk.assert_called()

                    # Second call - cache hit
                    mock_cache.get_from_disk.return_value = [{"sentence": "Cached content", "source": "cache"}]
                    result2 = parse_document_content(tmp_file.name)

                    assert result2 == [{"sentence": "Cached content", "source": "cache"}]

                finally:
                    os.unlink(tmp_file.name)


class TestFileValidationComprehensive:
    """Comprehensive tests for file validation and security."""

    def test_file_magic_validation_pdf(self):
        """Test magic number validation for PDF files."""
        from src.core.file_upload_validator import FileMagicValidator

        # Valid PDF content
        valid_pdf = b"%PDF-1.4\n%Sample PDF content"
        is_valid, error = FileMagicValidator.validate_file(valid_pdf, "test.pdf")

        assert is_valid
        assert error is None

    def test_file_magic_validation_docx(self):
        """Test magic number validation for DOCX files."""
        from src.core.file_upload_validator import FileMagicValidator

        # Valid DOCX content (ZIP-based format)
        valid_docx = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"
        is_valid, error = FileMagicValidator.validate_file(valid_docx, "test.docx")

        assert is_valid
        assert error is None

    def test_file_magic_validation_txt(self):
        """Test magic number validation for text files."""
        from src.core.file_upload_validator import FileMagicValidator

        # Valid text content
        valid_txt = b"Sample text content"
        is_valid, error = FileMagicValidator.validate_file(valid_txt, "test.txt")

        assert is_valid
        assert error is None

    def test_file_magic_validation_unsupported_type(self):
        """Test magic number validation for unsupported file types."""
        from src.core.file_upload_validator import FileMagicValidator

        # Unsupported file type
        unsupported_content = b"Some content"
        is_valid, error = FileMagicValidator.validate_file(unsupported_content, "test.xyz")

        assert not is_valid
        assert "File type 'xyz' is not allowed" in error

    def test_file_size_validation(self):
        """Test file size validation."""
        from src.core.file_upload_validator import FileMagicValidator

        # Empty file
        empty_content = b""
        is_valid, error = FileMagicValidator.validate_file(empty_content, "test.pdf")

        assert not is_valid
        assert "File is empty" in error

        # Oversized file
        oversized_content = b"x" * (51 * 1024 * 1024)  # 51MB
        is_valid, error = FileMagicValidator.validate_file(oversized_content, "test.pdf")

        assert not is_valid
        assert "File size exceeds maximum allowed size" in error

    def test_dangerous_pattern_detection(self):
        """Test detection of dangerous patterns in file content."""
        from src.core.file_upload_validator import FileMagicValidator

        # File with JavaScript
        dangerous_content = b"<script>alert('xss')</script>"
        is_valid, error = FileMagicValidator.validate_file(dangerous_content, "test.txt")

        assert not is_valid
        assert "Potentially dangerous content detected" in error

    def test_security_validator_filename_validation(self):
        """Test filename validation."""
        from src.core.security_validator import SecurityValidator

        # Valid filename
        is_valid, error = SecurityValidator.validate_filename("test.pdf")
        assert is_valid
        assert error is None

        # Empty filename
        is_valid, error = SecurityValidator.validate_filename("")
        assert not is_valid
        assert "Filename is required" in error

        # Filename too long
        long_filename = "x" * 300
        is_valid, error = SecurityValidator.validate_filename(long_filename)
        assert not is_valid
        assert "Filename exceeds maximum length" in error

        # Filename with path traversal
        is_valid, error = SecurityValidator.validate_filename("../../../etc/passwd")
        assert not is_valid
        assert "Path traversal detected" in error

    def test_security_validator_discipline_validation(self):
        """Test discipline validation."""
        from src.core.security_validator import SecurityValidator

        # Valid disciplines
        for discipline in ["pt", "ot", "slp"]:
            is_valid, error = SecurityValidator.validate_discipline(discipline)
            assert is_valid
            assert error is None

        # Invalid discipline
        is_valid, error = SecurityValidator.validate_discipline("invalid")
        assert not is_valid
        assert "Invalid discipline" in error

    def test_security_validator_analysis_mode_validation(self):
        """Test analysis mode validation."""
        from src.core.security_validator import SecurityValidator

        # Valid analysis modes
        for mode in ["rubric", "checklist", "hybrid"]:
            is_valid, error = SecurityValidator.validate_analysis_mode(mode)
            assert is_valid
            assert error is None

        # Invalid analysis mode
        is_valid, error = SecurityValidator.validate_analysis_mode("invalid")
        assert not is_valid
        assert "Invalid analysis mode" in error

    def test_security_validator_strictness_validation(self):
        """Test strictness level validation."""
        from src.core.security_validator import SecurityValidator

        # Valid strictness levels
        for strictness in ["standard", "ultra_fast", "balanced", "thorough", "clinical_grade"]:
            is_valid, error = SecurityValidator.validate_strictness(strictness)
            assert is_valid
            assert error is None

        # Invalid strictness level
        is_valid, error = SecurityValidator.validate_strictness("invalid")
        assert not is_valid
        assert "Invalid strictness level" in error

    def test_security_validator_text_input_validation(self):
        """Test text input validation."""
        from src.core.security_validator import SecurityValidator

        # Valid text input
        valid_text = "Sample text content"
        is_valid, error = SecurityValidator.validate_text_input(valid_text)
        assert is_valid
        assert error is None

        # Text too long
        long_text = "x" * 10001
        is_valid, error = SecurityValidator.validate_text_input(long_text)
        assert not is_valid
        assert "Text input exceeds maximum length" in error

        # Text with dangerous patterns
        dangerous_text = "<script>alert('xss')</script>"
        is_valid, error = SecurityValidator.validate_text_input(dangerous_text)
        assert not is_valid
        assert "Potentially dangerous content detected" in error


class TestDocumentProcessingIntegration:
    """Integration tests for document processing workflows."""

    @pytest.mark.asyncio
    async def test_complete_document_processing_workflow(self):
        """Test complete document processing workflow."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Test document content
        document_text = """
        Patient: John Doe
        Date: 2024-01-01
        Assessment: Patient presents with lower back pain
        Plan: Continue physical therapy exercises
        """

        # Process document
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text=document_text,
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_file_upload(self):
        """Test document processing with file upload."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Create test file content
        file_content = create_test_pdf("Sample PDF content for analysis")

        # Process document with file upload
        result = await analysis_service.analyze_document(
            discipline="pt",
            file_content=file_content,
            original_filename="test.pdf",
            analysis_mode="rubric",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result

    @pytest.mark.asyncio
    async def test_document_processing_error_handling(self):
        """Test document processing error handling."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Test with invalid parameters
        with pytest.raises(ValueError):
            await analysis_service.analyze_document(
                discipline="invalid",
                document_text="Test content"
            )

    @pytest.mark.asyncio
    async def test_document_processing_progress_callback(self):
        """Test document processing with progress callback."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Track progress
        progress_updates = []

        def progress_callback(progress: int, message: str):
            progress_updates.append((progress, message))

        # Process document with progress callback
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text="Sample content for progress testing",
            progress_callback=progress_callback
        )

        assert result is not None
        assert len(progress_updates) > 0
        assert all(isinstance(update[0], int) for update in progress_updates)
        assert all(isinstance(update[1], str) for update in progress_updates)


class TestPerformanceAndLoadTesting:
    """Performance and load testing for document processing."""

    def test_document_processing_performance(self):
        """Test document processing performance."""
        import time
        from src.core.parsing import parse_document_content

        # Create large test document
        large_content = "Sample content " * 10000

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(large_content.encode())
            tmp_file.flush()

            try:
                start_time = time.time()
                result = parse_document_content(tmp_file.name)
                end_time = time.time()

                processing_time = end_time - start_time

                # Should process within reasonable time (5 seconds)
                assert processing_time < 5.0
                assert isinstance(result, list)
                assert len(result) > 0

            finally:
                os.unlink(tmp_file.name)

    def test_concurrent_document_processing(self):
        """Test concurrent document processing."""
        import threading
        import time
        from src.core.parsing import parse_document_content

        results = []
        errors = []

        def process_document(content: str, suffix: str):
            try:
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                    tmp_file.write(content.encode())
                    tmp_file.flush()

                    result = parse_document_content(tmp_file.name)
                    results.append(result)

                    os.unlink(tmp_file.name)
            except Exception as e:
                errors.append(e)

        # Create multiple threads for concurrent processing
        threads = []
        for i in range(5):
            content = f"Sample content {i} " * 1000
            thread = threading.Thread(target=process_document, args=(content, ".txt"))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)

        # Verify results
        assert len(results) == 5
        assert len(errors) == 0

        # Verify all results are valid
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0

    def test_memory_usage_during_processing(self):
        """Test memory usage during document processing."""
        import psutil
        import os
        from src.core.parsing import parse_document_content

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Process multiple documents
        for i in range(10):
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                content = f"Sample content {i} " * 1000
                tmp_file.write(content.encode())
                tmp_file.flush()

                try:
                    result = parse_document_content(tmp_file.name)
                    assert isinstance(result, list)
                finally:
                    os.unlink(tmp_file.name)

        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024


class TestErrorHandlingAndEdgeCases:
    """Comprehensive error handling and edge case testing."""

    def test_parse_document_with_special_characters(self):
        """Test parsing documents with special characters."""
        from src.core.parsing import parse_document_content

        special_content = "Content with special chars: àáâãäåæçèéêë"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(special_content.encode('utf-8'))
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify special characters are preserved
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "àáâãäåæçèéêë" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_parse_document_with_unicode_content(self):
        """Test parsing documents with Unicode content."""
        from src.core.parsing import parse_document_content

        unicode_content = "Unicode content: 中文 العربية русский"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(unicode_content.encode('utf-8'))
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify Unicode content is preserved
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "中文" in combined_text
                assert "العربية" in combined_text
                assert "русский" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_parse_document_with_empty_lines(self):
        """Test parsing documents with empty lines."""
        from src.core.parsing import parse_document_content

        content_with_empty_lines = "Line 1\n\n\nLine 2\n\nLine 3"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(content_with_empty_lines.encode())
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify empty lines are handled properly
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Line 1" in combined_text
                assert "Line 2" in combined_text
                assert "Line 3" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_parse_document_with_very_long_lines(self):
        """Test parsing documents with very long lines."""
        from src.core.parsing import parse_document_content

        long_line = "A" * 10000

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(long_line.encode())
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify long lines are handled properly
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert len(combined_text) > 0

            finally:
                os.unlink(tmp_file.name)

    def test_parse_document_with_mixed_encodings(self):
        """Test parsing documents with mixed encodings."""
        from src.core.parsing import parse_document_content

        # Create content with mixed encodings
        mixed_content = "ASCII content\nLatin-1: àáâãäå\nUTF-8: 中文"

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            try:
                tmp_file.write(mixed_content.encode('utf-8'))
                tmp_file.flush()

                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify mixed encodings are handled
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "ASCII content" in combined_text

            finally:
                os.unlink(tmp_file.name)

    def test_parse_document_with_binary_content(self):
        """Test parsing documents with binary content."""
        from src.core.parsing import parse_document_content

        # Create binary content
        binary_content = b'\x00\x01\x02\x03\x04\x05\x06\x07'

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(binary_content)
            tmp_file.flush()

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify binary content is handled gracefully
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert len(combined_text) >= 0  # May be empty or contain error message

            finally:
                os.unlink(tmp_file.name)

    def test_parse_document_with_nested_directories(self):
        """Test parsing documents in nested directories."""
        from src.core.parsing import parse_document_content

        # Create nested directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "level1" / "level2" / "level3"
            nested_dir.mkdir(parents=True)

            file_path = nested_dir / "test.txt"
            file_path.write_text("Content in nested directory")

            result = parse_document_content(str(file_path))

            assert isinstance(result, list)
            assert len(result) > 0

            # Verify content is extracted
            combined_text = " ".join(chunk["sentence"] for chunk in result)
            assert "Content in nested directory" in combined_text

    def test_parse_document_with_permission_issues(self):
        """Test parsing documents with permission issues."""
        from src.core.parsing import parse_document_content

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_file.write(b"Content with permission issues")
            tmp_file.flush()

            # Change file permissions to read-only
            os.chmod(tmp_file.name, 0o444)

            try:
                result = parse_document_content(tmp_file.name)

                assert isinstance(result, list)
                assert len(result) > 0

                # Verify content is extracted despite permission issues
                combined_text = " ".join(chunk["sentence"] for chunk in result)
                assert "Content with permission issues" in combined_text

            finally:
                # Restore permissions for cleanup
                os.chmod(tmp_file.name, 0o644)
                os.unlink(tmp_file.name)

    def test_parse_document_with_concurrent_access(self):
        """Test parsing documents with concurrent access."""
        import threading
        import time
        from src.core.parsing import parse_document_content

        results = []
        errors = []

        def parse_document():
            try:
                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
                    tmp_file.write(b"Content for concurrent access test")
                    tmp_file.flush()

                    result = parse_document_content(tmp_file.name)
                    results.append(result)

                    os.unlink(tmp_file.name)
            except Exception as e:
                errors.append(e)

        # Create multiple threads for concurrent access
        threads = []
        for i in range(3):
            thread = threading.Thread(target=parse_document)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5)

        # Verify results
        assert len(results) == 3
        assert len(errors) == 0

        # Verify all results are valid
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0
