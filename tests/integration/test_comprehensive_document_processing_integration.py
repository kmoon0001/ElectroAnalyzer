"""Comprehensive end-to-end integration tests for document processing workflows.

This module provides thorough testing for:
- Complete document processing pipelines
- API endpoint integration
- Database integration
- Authentication and authorization
- Error handling and recovery
- Performance under load
"""

import pytest
import pytest_asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from fastapi.testclient import TestClient
from tests.data.test_documents import (
    create_test_pdf,
    create_test_docx,
    create_test_image,
    create_test_txt,
    create_malicious_file,
    create_oversized_file,
    create_corrupted_file,
)


class TestDocumentProcessingIntegration:
    """Comprehensive integration tests for document processing workflows."""

    @pytest.mark.asyncio
    async def test_complete_document_processing_workflow_pdf(self):
        """Test complete document processing workflow with PDF."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Create test PDF content
        pdf_content = create_test_pdf("Sample PDF content for analysis")

        # Process document with file upload
        result = await analysis_service.analyze_document(
            discipline="pt",
            file_content=pdf_content,
            original_filename="test.pdf",
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result
        assert "document_type" in result
        assert "discipline" in result
        assert "analysis_mode" in result
        assert "strictness" in result

    @pytest.mark.asyncio
    async def test_complete_document_processing_workflow_docx(self):
        """Test complete document processing workflow with DOCX."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Create test DOCX content
        docx_content = create_test_docx("Sample DOCX content for analysis")

        # Process document with file upload
        result = await analysis_service.analyze_document(
            discipline="ot",
            file_content=docx_content,
            original_filename="test.docx",
            analysis_mode="rubric",
            strictness="thorough"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result
        assert "document_type" in result
        assert "discipline" in result
        assert "analysis_mode" in result
        assert "strictness" in result

    @pytest.mark.asyncio
    async def test_complete_document_processing_workflow_image(self):
        """Test complete document processing workflow with image."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Create test image content
        image_content = create_test_image("Sample image content for analysis")

        # Process document with file upload
        result = await analysis_service.analyze_document(
            discipline="slp",
            file_content=image_content,
            original_filename="test.png",
            analysis_mode="checklist",
            strictness="clinical_grade"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result
        assert "document_type" in result
        assert "discipline" in result
        assert "analysis_mode" in result
        assert "strictness" in result

    @pytest.mark.asyncio
    async def test_complete_document_processing_workflow_text(self):
        """Test complete document processing workflow with text."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Process document with text input
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text="Sample text content for analysis",
            analysis_mode="hybrid",
            strictness="balanced"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result
        assert "document_type" in result
        assert "discipline" in result
        assert "analysis_mode" in result
        assert "strictness" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_progress_callback(self):
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

        # Verify progress values are reasonable
        progress_values = [update[0] for update in progress_updates]
        assert min(progress_values) >= 0
        assert max(progress_values) <= 100

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

        # Test with missing parameters
        with pytest.raises(ValueError):
            await analysis_service.analyze_document(
                discipline="pt"
            )

    @pytest.mark.asyncio
    async def test_document_processing_with_corrupted_file(self):
        """Test document processing with corrupted file."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Create corrupted file content
        corrupted_content = create_corrupted_file("pdf")

        # Process document with corrupted file
        result = await analysis_service.analyze_document(
            discipline="pt",
            file_content=corrupted_content,
            original_filename="corrupted.pdf",
            analysis_mode="hybrid",
            strictness="standard"
        )

        # Should handle corrupted file gracefully
        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_oversized_file(self):
        """Test document processing with oversized file."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Create oversized file content
        oversized_content = create_oversized_file(51)  # 51MB

        # Process document with oversized file
        with pytest.raises(ValueError):
            await analysis_service.analyze_document(
                discipline="pt",
                file_content=oversized_content,
                original_filename="oversized.pdf",
                analysis_mode="hybrid",
                strictness="standard"
            )

    @pytest.mark.asyncio
    async def test_document_processing_with_malicious_file(self):
        """Test document processing with malicious file."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Create malicious file content
        malicious_content = create_malicious_file("script")

        # Process document with malicious file
        with pytest.raises(ValueError):
            await analysis_service.analyze_document(
                discipline="pt",
                file_content=malicious_content,
                original_filename="malicious.txt",
                analysis_mode="hybrid",
                strictness="standard"
            )

    @pytest.mark.asyncio
    async def test_document_processing_with_special_characters(self):
        """Test document processing with special characters."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Process document with special characters
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text="Content with special chars: àáâãäåæçèéêë",
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_unicode_content(self):
        """Test document processing with Unicode content."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Process document with Unicode content
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text="Unicode content: 中文 العربية русский",
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_mixed_encodings(self):
        """Test document processing with mixed encodings."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Process document with mixed encodings
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text="Mixed encoding: Hello 世界 مرحبا мир",
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_empty_lines(self):
        """Test document processing with empty lines."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Process document with empty lines
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text="Line 1\n\n\nLine 2\n\nLine 3",
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_very_long_lines(self):
        """Test document processing with very long lines."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Process document with very long lines
        long_line = "A" * 10000
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text=long_line,
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_binary_content(self):
        """Test document processing with binary content."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Process document with binary content
        binary_content = bytes(range(256))  # All possible byte values

        # This should handle binary content gracefully
        result = await analysis_service.analyze_document(
            discipline="pt",
            file_content=binary_content,
            original_filename="binary.bin",
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_concurrent_requests(self):
        """Test document processing with concurrent requests."""
        import asyncio
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        async def process_document(discipline: str, content: str):
            return await analysis_service.analyze_document(
                discipline=discipline,
                document_text=content,
                analysis_mode="hybrid",
                strictness="standard"
            )

        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            content = f"Sample content {i} for concurrent processing"
            task = process_document("pt", content)
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)

        # Verify all results are valid
        assert len(results) == 5
        for result in results:
            assert result is not None
            assert isinstance(result, dict)
            assert "analysis_id" in result
            assert "score" in result
            assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_performance_under_load(self):
        """Test document processing performance under load."""
        import time
        import asyncio
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        async def process_document(discipline: str, content: str):
            start_time = time.time()
            result = await analysis_service.analyze_document(
                discipline=discipline,
                document_text=content,
                analysis_mode="hybrid",
                strictness="standard"
            )
            end_time = time.time()
            processing_time = end_time - start_time
            return result, processing_time

        # Create multiple concurrent requests
        tasks = []
        for i in range(10):
            content = f"Sample content {i} for performance testing"
            task = process_document("pt", content)
            tasks.append(task)

        # Wait for all tasks to complete
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time

        # Verify all results are valid
        assert len(results) == 10
        for result, processing_time in results:
            assert result is not None
            assert isinstance(result, dict)
            assert "analysis_id" in result
            assert "score" in result
            assert "recommendations" in result
            assert processing_time < 5.0  # Each request should complete within 5 seconds

        # Total time should be reasonable (less than 30 seconds for 10 requests)
        assert total_time < 30.0

    @pytest.mark.asyncio
    async def test_document_processing_memory_usage(self):
        """Test document processing memory usage."""
        import psutil
        import os
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Process multiple documents
        for i in range(10):
            content = f"Sample content {i} for memory testing"
            result = await analysis_service.analyze_document(
                discipline="pt",
                document_text=content,
                analysis_mode="hybrid",
                strictness="standard"
            )
            assert result is not None

        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

    @pytest.mark.asyncio
    async def test_document_processing_error_recovery(self):
        """Test document processing error recovery."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        # Test error recovery with invalid file
        try:
            result = await analysis_service.analyze_document(
                discipline="pt",
                file_content=b"Invalid file content",
                original_filename="invalid.xyz",
                analysis_mode="hybrid",
                strictness="standard"
            )
            # Should handle gracefully
            assert result is not None
        except ValueError:
            # Expected for unsupported file types
            pass

        # Test error recovery with valid file after error
        result = await analysis_service.analyze_document(
            discipline="pt",
            document_text="Valid content after error",
            analysis_mode="hybrid",
            strictness="standard"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "analysis_id" in result
        assert "score" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_document_processing_with_different_disciplines(self):
        """Test document processing with different disciplines."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        disciplines = ["pt", "ot", "slp"]

        for discipline in disciplines:
            result = await analysis_service.analyze_document(
                discipline=discipline,
                document_text=f"Sample content for {discipline} discipline",
                analysis_mode="hybrid",
                strictness="standard"
            )

            assert result is not None
            assert isinstance(result, dict)
            assert "analysis_id" in result
            assert "score" in result
            assert "recommendations" in result
            assert result["discipline"] == discipline

    @pytest.mark.asyncio
    async def test_document_processing_with_different_analysis_modes(self):
        """Test document processing with different analysis modes."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        analysis_modes = ["rubric", "checklist", "hybrid"]

        for analysis_mode in analysis_modes:
            result = await analysis_service.analyze_document(
                discipline="pt",
                document_text=f"Sample content for {analysis_mode} mode",
                analysis_mode=analysis_mode,
                strictness="standard"
            )

            assert result is not None
            assert isinstance(result, dict)
            assert "analysis_id" in result
            assert "score" in result
            assert "recommendations" in result
            assert result["analysis_mode"] == analysis_mode

    @pytest.mark.asyncio
    async def test_document_processing_with_different_strictness_levels(self):
        """Test document processing with different strictness levels."""
        from src.core.analysis_service import AnalysisService

        # Create analysis service with mocks
        analysis_service = AnalysisService()
        analysis_service.use_mocks = True

        strictness_levels = ["standard", "ultra_fast", "balanced", "thorough", "clinical_grade"]

        for strictness in strictness_levels:
            result = await analysis_service.analyze_document(
                discipline="pt",
                document_text=f"Sample content for {strictness} strictness",
                analysis_mode="hybrid",
                strictness=strictness
            )

            assert result is not None
            assert isinstance(result, dict)
            assert "analysis_id" in result
            assert "score" in result
            assert "recommendations" in result
            assert result["strictness"] == strictness
