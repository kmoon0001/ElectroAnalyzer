"""Fixed comprehensive document processing tests with proper file handling."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from tests.data.test_documents import TestDocumentData


class TestDocumentParsingComprehensive:
    """Comprehensive tests for document parsing across all supported formats."""

    def setup_method(self):
        """Set up test data."""
        self.test_data = TestDocumentData()

    def _create_temp_file(self, content: bytes, suffix: str) -> str:
        """Create a temporary file with proper cleanup."""
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            return tmp_file.name

    def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary file with proper error handling."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except PermissionError:
            # On Windows, sometimes we need to wait a bit
            import time
            time.sleep(0.1)
            try:
                os.unlink(file_path)
            except PermissionError:
                # File will be cleaned up by system eventually
                pass

    def test_parse_pdf_with_text_content(self):
        """Test PDF parsing with text content."""
        from src.core.parsing import parse_document_content

        # Create temporary PDF file
        pdf_content = self.test_data.create_test_pdf("Sample PDF content for testing")
        tmp_path = self._create_temp_file(pdf_content, ".pdf")

        try:
            result = parse_document_content(tmp_path)

            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(chunk, dict) for chunk in result)
            assert all("sentence" in chunk for chunk in result)
            assert all("source" in chunk for chunk in result)

            # Verify content extraction
            combined_text = " ".join(chunk["sentence"] for chunk in result)
            assert "Sample PDF content" in combined_text

        finally:
            self._cleanup_temp_file(tmp_path)

    def test_parse_pdf_with_images_ocr(self):
        """Test PDF parsing with OCR for image content."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.OCR_AVAILABLE', True):
            with patch('src.core.parsing.pytesseract') as mock_tesseract:
                mock_tesseract.image_to_string.return_value = "OCR extracted text"

                # Create temporary PDF file
                pdf_content = self.test_data.create_test_pdf("Sample PDF with images")
                tmp_path = self._create_temp_file(pdf_content, ".pdf")

                try:
                    result = parse_document_content(tmp_path)

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert all(isinstance(chunk, dict) for chunk in result)

                finally:
                    self._cleanup_temp_file(tmp_path)

    def test_parse_docx_content(self):
        """Test DOCX parsing."""
        from src.core.parsing import parse_document_content

        # Create temporary DOCX file
        docx_content = self.test_data.create_test_docx("Sample DOCX content")
        tmp_path = self._create_temp_file(docx_content, ".docx")

        try:
            result = parse_document_content(tmp_path)

            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(chunk, dict) for chunk in result)
            assert all("sentence" in chunk for chunk in result)

            # Verify content extraction
            combined_text = " ".join(chunk["sentence"] for chunk in result)
            assert "Sample DOCX content" in combined_text

        finally:
            self._cleanup_temp_file(tmp_path)

    def test_parse_image_with_ocr(self):
        """Test image parsing with OCR."""
        from src.core.parsing import parse_document_content

        with patch('src.core.parsing.OCR_AVAILABLE', True):
            with patch('src.core.parsing.pytesseract') as mock_tesseract:
                mock_tesseract.image_to_string.return_value = "OCR extracted text from image"

                # Create temporary image file
                image_content = self.test_data.create_test_image()
                tmp_path = self._create_temp_file(image_content, ".png")

                try:
                    result = parse_document_content(tmp_path)

                    assert isinstance(result, list)
                    assert len(result) > 0
                    assert all(isinstance(chunk, dict) for chunk in result)

                finally:
                    self._cleanup_temp_file(tmp_path)

    def test_parse_text_file(self):
        """Test text file parsing."""
        from src.core.parsing import parse_document_content

        # Create temporary text file
        text_content = "Sample text content for testing".encode('utf-8')
        tmp_path = self._create_temp_file(text_content, ".txt")

        try:
            result = parse_document_content(tmp_path)

            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(chunk, dict) for chunk in result)
            assert all("sentence" in chunk for chunk in result)

            # Verify content extraction
            combined_text = " ".join(chunk["sentence"] for chunk in result)
            assert "Sample text content" in combined_text

        finally:
            self._cleanup_temp_file(tmp_path)

    def test_parse_unsupported_file_type(self):
        """Test parsing of unsupported file types."""
        from src.core.parsing import parse_document_content

        # Create temporary file with unsupported extension
        content = b"Some content"
        tmp_path = self._create_temp_file(content, ".xyz")

        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                parse_document_content(tmp_path)

        finally:
            self._cleanup_temp_file(tmp_path)

    def test_parse_nonexistent_file(self):
        """Test parsing of nonexistent file."""
        from src.core.parsing import parse_document_content

        with pytest.raises(FileNotFoundError):
            parse_document_content("nonexistent_file.pdf")

    def test_parse_empty_file(self):
        """Test parsing of empty file."""
        from src.core.parsing import parse_document_content

        # Create empty temporary file
        tmp_path = self._create_temp_file(b"", ".txt")

        try:
            result = parse_document_content(tmp_path)
            assert isinstance(result, list)
            assert len(result) == 0

        finally:
            self._cleanup_temp_file(tmp_path)

    def test_parse_corrupted_file(self):
        """Test parsing of corrupted file."""
        from src.core.parsing import parse_document_content

        # Create corrupted file
        corrupted_content = b"This is not a valid PDF file"
        tmp_path = self._create_temp_file(corrupted_content, ".pdf")

        try:
            # Should handle corruption gracefully
            result = parse_document_content(tmp_path)
            assert isinstance(result, list)

        finally:
            self._cleanup_temp_file(tmp_path)

    def test_parse_large_file(self):
        """Test parsing of large file."""
        from src.core.parsing import parse_document_content

        # Create large text file
        large_content = ("Sample text content " * 1000).encode('utf-8')
        tmp_path = self._create_temp_file(large_content, ".txt")

        try:
            result = parse_document_content(tmp_path)

            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(chunk, dict) for chunk in result)

        finally:
            self._cleanup_temp_file(tmp_path)

    def test_parse_file_with_special_characters(self):
        """Test parsing of file with special characters."""
        from src.core.parsing import parse_document_content

        # Create file with special characters
        special_content = "Special chars: àáâãäåæçèéêë ñöøùúûü ýþÿ".encode('utf-8')
        tmp_path = self._create_temp_file(special_content, ".txt")

        try:
            result = parse_document_content(tmp_path)

            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(chunk, dict) for chunk in result)

        finally:
            self._cleanup_temp_file(tmp_path)

    def test_parse_file_with_unicode(self):
        """Test parsing of file with Unicode characters."""
        from src.core.parsing import parse_document_content

        # Create file with Unicode characters
        unicode_content = "Unicode: 🚀🌟💡🎯📊".encode('utf-8')
        tmp_path = self._create_temp_file(unicode_content, ".txt")

        try:
            result = parse_document_content(tmp_path)

            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(chunk, dict) for chunk in result)

        finally:
            self._cleanup_temp_file(tmp_path)
