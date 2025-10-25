"""Comprehensive test configuration for document processing tests.

This module provides:
- Test configuration and setup
- Test data management
- Test utilities and helpers
- Mock configurations
- Test environment setup
"""

import pytest
import pytest_asyncio
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List


# Test configuration
TEST_CONFIG = {
    "test_data_dir": "tests/data",
    "temp_dir": "tests/temp",
    "coverage_threshold": 80.0,
    "performance_timeout": 300,  # 5 minutes
    "memory_limit_mb": 100,
    "max_file_size_mb": 50,
    "supported_file_types": [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"],
    "test_disciplines": ["pt", "ot", "slp"],
    "test_analysis_modes": ["rubric", "checklist", "hybrid"],
    "test_strictness_levels": ["standard", "ultra_fast", "balanced", "thorough", "clinical_grade"],
}


class TestConfig:
    """Test configuration manager."""

    def __init__(self):
        self.config = TEST_CONFIG.copy()
        self._setup_test_environment()

    def _setup_test_environment(self):
        """Set up test environment."""
        # Create test directories
        test_data_dir = Path(self.config["test_data_dir"])
        test_data_dir.mkdir(parents=True, exist_ok=True)

        temp_dir = Path(self.config["temp_dir"])
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Set up environment variables
        os.environ["TESTING"] = "true"
        os.environ["USE_AI_MOCKS"] = "true"
        os.environ["LOG_LEVEL"] = "WARNING"

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value


# Global test configuration instance
test_config = TestConfig()


@pytest.fixture(scope="session")
def test_config_fixture():
    """Test configuration fixture."""
    return test_config


@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory fixture."""
    return Path(test_config.get_config("test_data_dir"))


@pytest.fixture(scope="session")
def temp_dir():
    """Temporary directory fixture."""
    return Path(test_config.get_config("temp_dir"))


@pytest.fixture(scope="function")
def temp_file():
    """Temporary file fixture."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        yield tmp_file.name
        try:
            os.unlink(tmp_file.name)
        except OSError:
            pass


@pytest.fixture(scope="function")
def temp_dir_cleanup():
    """Temporary directory cleanup fixture."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture(scope="function")
def mock_ai_services():
    """Mock AI services fixture."""
    with patch('src.core.analysis_service.AnalysisService.use_mocks', True):
        yield


@pytest.fixture(scope="function")
def mock_file_validation():
    """Mock file validation fixture."""
    with patch('src.core.file_upload_validator.FileMagicValidator.validate_file') as mock_validate:
        mock_validate.return_value = (True, None)
        yield mock_validate


@pytest.fixture(scope="function")
def mock_security_validation():
    """Mock security validation fixture."""
    with patch('src.core.security_validator.SecurityValidator.validate_filename') as mock_validate:
        mock_validate.return_value = (True, None)
        yield mock_validate


@pytest.fixture(scope="function")
def mock_document_parsing():
    """Mock document parsing fixture."""
    with patch('src.core.parsing.parse_document_content') as mock_parse:
        mock_parse.return_value = [
            {"sentence": "Mock parsed content", "source": "mock"}
        ]
        yield mock_parse


@pytest.fixture(scope="function")
def mock_ocr_services():
    """Mock OCR services fixture."""
    with patch('src.core.parsing.OCR_AVAILABLE', True):
        with patch('src.core.parsing.pytesseract') as mock_tesseract:
            mock_tesseract.image_to_string.return_value = "Mock OCR text"
            yield mock_tesseract


@pytest.fixture(scope="function")
def mock_pdf_processing():
    """Mock PDF processing fixture."""
    with patch('src.core.parsing.pdfplumber') as mock_pdfplumber:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Mock PDF text"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        yield mock_pdfplumber


@pytest.fixture(scope="function")
def mock_docx_processing():
    """Mock DOCX processing fixture."""
    with patch('src.core.parsing.Document') as mock_document:
        mock_para = MagicMock()
        mock_para.text = "Mock DOCX text"
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para]
        mock_document.return_value = mock_doc
        yield mock_document


@pytest.fixture(scope="function")
def mock_image_processing():
    """Mock image processing fixture."""
    with patch('src.core.parsing.Image') as mock_image:
        mock_img = MagicMock()
        mock_img.size = (200, 100)
        mock_image.open.return_value = mock_img
        yield mock_image


@pytest.fixture(scope="function")
def mock_cache_service():
    """Mock cache service fixture."""
    with patch('src.core.parsing.cache_service') as mock_cache:
        mock_cache.get_from_disk.return_value = None
        mock_cache.set_to_disk.return_value = None
        yield mock_cache


@pytest.fixture(scope="function")
def mock_logging():
    """Mock logging fixture."""
    with patch('src.core.parsing.logger') as mock_logger:
        yield mock_logger


@pytest.fixture(scope="function")
def mock_os_operations():
    """Mock OS operations fixture."""
    with patch('src.core.parsing.os.path.exists') as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


@pytest.fixture(scope="function")
def mock_threading():
    """Mock threading fixture."""
    with patch('src.core.parsing.threading.Thread') as mock_thread:
        mock_thread.return_value.join.return_value = None
        mock_thread.return_value.is_alive.return_value = False
        yield mock_thread


@pytest.fixture(scope="function")
def mock_queue():
    """Mock queue fixture."""
    with patch('src.core.parsing.queue.Queue') as mock_queue:
        mock_queue.return_value.get_nowait.return_value = [
            {"sentence": "Mock queued content", "source": "mock"}
        ]
        yield mock_queue


@pytest.fixture(scope="function")
def mock_hashlib():
    """Mock hashlib fixture."""
    with patch('src.core.parsing.hashlib') as mock_hashlib:
        mock_hasher = MagicMock()
        mock_hasher.hexdigest.return_value = "mock_hash"
        mock_hashlib.sha256.return_value = mock_hasher
        yield mock_hashlib


@pytest.fixture(scope="function")
def mock_pathlib():
    """Mock pathlib fixture."""
    with patch('src.core.parsing.Path') as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        yield mock_path


@pytest.fixture(scope="function")
def mock_yaml():
    """Mock YAML fixture."""
    with patch('src.core.parsing.yaml') as mock_yaml:
        mock_yaml.safe_load.return_value = {"mock": "config"}
        yield mock_yaml


@pytest.fixture(scope="function")
def mock_pil():
    """Mock PIL fixture."""
    with patch('src.core.parsing.PIL') as mock_pil:
        mock_image = MagicMock()
        mock_image.size = (200, 100)
        mock_pil.Image.open.return_value = mock_image
        yield mock_pil


@pytest.fixture(scope="function")
def mock_numpy():
    """Mock numpy fixture."""
    with patch('src.core.parsing.np') as mock_np:
        mock_np.array.return_value = [[[255, 255, 255]] * 200] * 100
        yield mock_np


@pytest.fixture(scope="function")
def mock_cv2():
    """Mock OpenCV fixture."""
    with patch('src.core.parsing.cv2') as mock_cv2:
        mock_cv2.imread.return_value = None
        mock_cv2.cvtColor.return_value = None
        yield mock_cv2


@pytest.fixture(scope="function")
def mock_pytesseract():
    """Mock pytesseract fixture."""
    with patch('src.core.parsing.pytesseract') as mock_tesseract:
        mock_tesseract.image_to_string.return_value = "Mock OCR text"
        yield mock_tesseract


@pytest.fixture(scope="function")
def mock_docx():
    """Mock python-docx fixture."""
    with patch('src.core.parsing.Document') as mock_document:
        mock_para = MagicMock()
        mock_para.text = "Mock DOCX text"
        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para]
        mock_document.return_value = mock_doc
        yield mock_document


@pytest.fixture(scope="function")
def mock_pdfplumber():
    """Mock pdfplumber fixture."""
    with patch('src.core.parsing.pdfplumber') as mock_pdfplumber:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Mock PDF text"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        yield mock_pdfplumber


@pytest.fixture(scope="function")
def mock_psutil():
    """Mock psutil fixture."""
    with patch('src.core.parsing.psutil') as mock_psutil:
        mock_process = MagicMock()
        mock_process.memory_info.return_value = MagicMock(rss=100 * 1024 * 1024)  # 100MB
        mock_process.cpu_percent.return_value = 50.0
        mock_psutil.Process.return_value = mock_process
        yield mock_psutil


@pytest.fixture(scope="function")
def mock_signal():
    """Mock signal fixture."""
    with patch('src.core.parsing.signal') as mock_signal:
        mock_signal.signal.return_value = None
        yield mock_signal


@pytest.fixture(scope="function")
def mock_time():
    """Mock time fixture."""
    with patch('src.core.parsing.time') as mock_time:
        mock_time.time.return_value = 1000.0
        yield mock_time


@pytest.fixture(scope="function")
def mock_tempfile():
    """Mock tempfile fixture."""
    with patch('src.core.parsing.tempfile') as mock_tempfile:
        mock_tempfile.NamedTemporaryFile.return_value.__enter__.return_value.name = "/tmp/mock_file"
        yield mock_tempfile


@pytest.fixture(scope="function")
def mock_io():
    """Mock io fixture."""
    with patch('src.core.parsing.io') as mock_io:
        mock_buffer = MagicMock()
        mock_buffer.getvalue.return_value = b"mock content"
        mock_io.BytesIO.return_value = mock_buffer
        yield mock_io


@pytest.fixture(scope="function")
def mock_zipfile():
    """Mock zipfile fixture."""
    with patch('src.core.parsing.zipfile') as mock_zipfile:
        mock_zip = MagicMock()
        mock_zipfile.ZipFile.return_value.__enter__.return_value = mock_zip
        yield mock_zipfile


@pytest.fixture(scope="function")
def mock_path():
    """Mock pathlib.Path fixture."""
    with patch('src.core.parsing.Path') as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.mkdir.return_value = None
        mock_path.return_value.write_text.return_value = None
        mock_path.return_value.read_text.return_value = "mock content"
        yield mock_path


@pytest.fixture(scope="function")
def mock_os():
    """Mock os fixture."""
    with patch('src.core.parsing.os') as mock_os:
        mock_os.path.exists.return_value = True
        mock_os.path.splitext.return_value = ("file", ".txt")
        mock_os.path.basename.return_value = "file.txt"
        mock_os.chmod.return_value = None
        mock_os.mkdir.return_value = None
        mock_os.mknod.return_value = None
        mock_os.mkfifo.return_value = None
        yield mock_os


@pytest.fixture(scope="function")
def mock_re():
    """Mock re fixture."""
    with patch('src.core.parsing.re') as mock_re:
        mock_re.search.return_value = None
        mock_re.findall.return_value = []
        yield mock_re


@pytest.fixture(scope="function")
def mock_logging_module():
    """Mock logging module fixture."""
    with patch('src.core.parsing.logging') as mock_logging:
        mock_logger = MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        yield mock_logging


@pytest.fixture(scope="function")
def mock_sys():
    """Mock sys fixture."""
    with patch('src.core.parsing.sys') as mock_sys:
        mock_sys.path.insert.return_value = None
        yield mock_sys


@pytest.fixture(scope="function")
def mock_inspect():
    """Mock inspect fixture."""
    with patch('src.core.parsing.inspect') as mock_inspect:
        mock_inspect.iscoroutinefunction.return_value = False
        yield mock_inspect


@pytest.fixture(scope="function")
def mock_asyncio():
    """Mock asyncio fixture."""
    with patch('src.core.parsing.asyncio') as mock_asyncio:
        mock_asyncio.run.return_value = None
        yield mock_asyncio


@pytest.fixture(scope="function")
def mock_datetime():
    """Mock datetime fixture."""
    with patch('src.core.parsing.datetime') as mock_datetime:
        mock_datetime.datetime.utcnow.return_value = "2024-01-01T00:00:00Z"
        yield mock_datetime


@pytest.fixture(scope="function")
def mock_uuid():
    """Mock uuid fixture."""
    with patch('src.core.parsing.uuid') as mock_uuid:
        mock_uuid.uuid4.return_value = "mock-uuid"
        yield mock_uuid


@pytest.fixture(scope="function")
def mock_collections():
    """Mock collections fixture."""
    with patch('src.core.parsing.collections') as mock_collections:
        mock_collections.abc.Callable = MagicMock()
        yield mock_collections


@pytest.fixture(scope="function")
def mock_typing():
    """Mock typing fixture."""
    with patch('src.core.parsing.typing') as mock_typing:
        mock_typing.TYPE_CHECKING = False
        yield mock_typing


@pytest.fixture(scope="function")
def mock_src_config():
    """Mock src.config fixture."""
    with patch('src.core.parsing._get_settings') as mock_settings:
        mock_settings.return_value = MagicMock()
        yield mock_settings


@pytest.fixture(scope="function")
def mock_src_core():
    """Mock src.core modules fixture."""
    with patch('src.core.parsing.src.core') as mock_core:
        mock_core.analysis_utils = MagicMock()
        mock_core.cache_service = MagicMock()
        mock_core.checklist_service = MagicMock()
        mock_core.document_chunker = MagicMock()
        mock_core.explanation = MagicMock()
        mock_core.unified_explanation_engine = MagicMock()
        mock_core.file_cleanup_service = MagicMock()
        mock_core.model_selection_utils = MagicMock()
        mock_core.phi_scrubber = MagicMock()
        mock_core.preprocessing_service = MagicMock()
        mock_core.report_generator = MagicMock()
        mock_core.rubric_detector = MagicMock()
        mock_core.advanced_ensemble_optimizer = MagicMock()
        mock_core.multi_tier_cache = MagicMock()
        mock_core.clinical_education_engine = MagicMock()
        mock_core.human_feedback_system = MagicMock()
        mock_core.text_utils = MagicMock()
        yield mock_core


@pytest.fixture(scope="function")
def mock_src_utils():
    """Mock src.utils modules fixture."""
    with patch('src.core.parsing.src.utils') as mock_utils:
        mock_utils.prompt_manager = MagicMock()
        yield mock_utils


@pytest.fixture(scope="function")
def mock_src_database():
    """Mock src.database modules fixture."""
    with patch('src.core.parsing.src.database') as mock_database:
        mock_database.models = MagicMock()
        mock_database.schemas = MagicMock()
        mock_database.crud = MagicMock()
        yield mock_database


@pytest.fixture(scope="function")
def mock_src_auth():
    """Mock src.auth modules fixture."""
    with patch('src.core.parsing.src.auth') as mock_auth:
        mock_auth.AuthService = MagicMock()
        yield mock_auth


@pytest.fixture(scope="function")
def mock_src_api():
    """Mock src.api modules fixture."""
    with patch('src.core.parsing.src.api') as mock_api:
        mock_api.main = MagicMock()
        mock_api.dependencies = MagicMock()
        mock_api.routers = MagicMock()
        yield mock_api


@pytest.fixture(scope="function")
def mock_src_core_llm():
    """Mock src.core.llm_service fixture."""
    with patch('src.core.parsing.src.core.llm_service') as mock_llm:
        mock_llm.LLMService = MagicMock()
        yield mock_llm


@pytest.fixture(scope="function")
def mock_src_core_hybrid_retriever():
    """Mock src.core.hybrid_retriever fixture."""
    with patch('src.core.parsing.src.core.hybrid_retriever') as mock_retriever:
        mock_retriever.HybridRetriever = MagicMock()
        yield mock_retriever


@pytest.fixture(scope="function")
def mock_src_core_ner():
    """Mock src.core.ner fixture."""
    with patch('src.core.parsing.src.core.ner') as mock_ner:
        mock_ner.ClinicalNERService = MagicMock()
        yield mock_ner


@pytest.fixture(scope="function")
def mock_src_core_nlg():
    """Mock src.core.nlg_service fixture."""
    with patch('src.core.parsing.src.core.nlg_service') as mock_nlg:
        mock_nlg.NLGService = MagicMock()
        yield mock_nlg


@pytest.fixture(scope="function")
def mock_src_core_document_classifier():
    """Mock src.core.document_classifier fixture."""
    with patch('src.core.parsing.src.core.document_classifier') as mock_classifier:
        mock_classifier.DocumentClassifier = MagicMock()
        yield mock_classifier


@pytest.fixture(scope="function")
def mock_src_core_fact_checker():
    """Mock src.core.fact_checker_service fixture."""
    with patch('src.core.parsing.src.core.fact_checker_service') as mock_fact_checker:
        mock_fact_checker.FactCheckerService = MagicMock()
        yield mock_fact_checker


@pytest.fixture(scope="function")
def mock_src_core_compliance_analyzer():
    """Mock src.core.compliance_analyzer fixture."""
    with patch('src.core.parsing.src.core.compliance_analyzer') as mock_compliance:
        mock_compliance.ComplianceAnalyzer = MagicMock()
        yield mock_compliance


# Test data fixtures
@pytest.fixture(scope="function")
def sample_pdf_content():
    """Sample PDF content fixture."""
    return b"%PDF-1.4\n%Sample PDF content"


@pytest.fixture(scope="function")
def sample_docx_content():
    """Sample DOCX content fixture."""
    return b"PK\x03\x04\x14\x00\x00\x00\x08\x00"


@pytest.fixture(scope="function")
def sample_txt_content():
    """Sample text content fixture."""
    return b"Sample text content"


@pytest.fixture(scope="function")
def sample_image_content():
    """Sample image content fixture."""
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"


@pytest.fixture(scope="function")
def sample_malicious_content():
    """Sample malicious content fixture."""
    return b"<script>alert('xss')</script>"


@pytest.fixture(scope="function")
def sample_oversized_content():
    """Sample oversized content fixture."""
    return b"x" * (51 * 1024 * 1024)  # 51MB


@pytest.fixture(scope="function")
def sample_corrupted_content():
    """Sample corrupted content fixture."""
    return b"Corrupted file content"


@pytest.fixture(scope="function")
def sample_special_characters_content():
    """Sample special characters content fixture."""
    return "Special characters: àáâãäåæçèéêë".encode('utf-8')


@pytest.fixture(scope="function")
def sample_unicode_content():
    """Sample Unicode content fixture."""
    return "Unicode content: 中文 العربية русский".encode('utf-8')


@pytest.fixture(scope="function")
def sample_mixed_encodings_content():
    """Sample mixed encodings content fixture."""
    return "Mixed encoding: Hello 世界 مرحبا мир".encode('utf-8')


@pytest.fixture(scope="function")
def sample_empty_lines_content():
    """Sample empty lines content fixture."""
    return "Line 1\n\n\nLine 2\n\nLine 3".encode('utf-8')


@pytest.fixture(scope="function")
def sample_very_long_lines_content():
    """Sample very long lines content fixture."""
    return ("A" * 10000).encode()


@pytest.fixture(scope="function")
def sample_binary_content():
    """Sample binary content fixture."""
    return bytes(range(256))


# Test utilities
class TestUtils:
    """Test utilities class."""

    @staticmethod
    def create_temp_file(content: bytes, suffix: str = ".txt") -> str:
        """Create a temporary file with content."""
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()
            return tmp_file.name

    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Clean up temporary file."""
        try:
            os.unlink(file_path)
        except OSError:
            pass

    @staticmethod
    def create_temp_dir() -> str:
        """Create a temporary directory."""
        return tempfile.mkdtemp()

    @staticmethod
    def cleanup_temp_dir(dir_path: str) -> None:
        """Clean up temporary directory."""
        try:
            import shutil
            shutil.rmtree(dir_path)
        except OSError:
            pass

    @staticmethod
    def assert_file_exists(file_path: str) -> None:
        """Assert that file exists."""
        assert os.path.exists(file_path), f"File {file_path} does not exist"

    @staticmethod
    def assert_file_not_exists(file_path: str) -> None:
        """Assert that file does not exist."""
        assert not os.path.exists(file_path), f"File {file_path} should not exist"

    @staticmethod
    def assert_file_content(file_path: str, expected_content: bytes) -> None:
        """Assert file content."""
        with open(file_path, 'rb') as f:
            actual_content = f.read()
        assert actual_content == expected_content, f"File content mismatch for {file_path}"

    @staticmethod
    def assert_file_size(file_path: str, expected_size: int) -> None:
        """Assert file size."""
        actual_size = os.path.getsize(file_path)
        assert actual_size == expected_size, f"File size mismatch for {file_path}: expected {expected_size}, got {actual_size}"


# Test data management
class TestDataManager:
    """Test data manager class."""

    def __init__(self, data_dir: str = "tests/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_test_file(self, filename: str, content: bytes) -> Path:
        """Create a test file."""
        file_path = self.data_dir / filename
        file_path.write_bytes(content)
        return file_path

    def get_test_file(self, filename: str) -> Path:
        """Get test file path."""
        return self.data_dir / filename

    def cleanup_test_files(self) -> None:
        """Clean up test files."""
        for file_path in self.data_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()

    def list_test_files(self) -> List[Path]:
        """List test files."""
        return list(self.data_dir.glob("*"))


# Global test data manager instance
test_data_manager = TestDataManager()


@pytest.fixture(scope="session")
def test_data_manager_fixture():
    """Test data manager fixture."""
    return test_data_manager


# Test configuration for pytest
def pytest_configure(config):
    """Configure pytest."""
    # Add custom markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "error_handling: Error handling tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "fast: Fast tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add markers based on test file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "error_handling" in str(item.fspath):
            item.add_marker(pytest.mark.error_handling)

        # Add slow marker for tests that take longer than 1 second
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.fast)


def pytest_runtest_setup(item):
    """Set up test run."""
    # Set up test environment
    os.environ["TESTING"] = "true"
    os.environ["USE_AI_MOCKS"] = "true"
    os.environ["LOG_LEVEL"] = "WARNING"


def pytest_runtest_teardown(item):
    """Tear down test run."""
    # Clean up test environment
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
    if "USE_AI_MOCKS" in os.environ:
        del os.environ["USE_AI_MOCKS"]
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]


def pytest_report_header(config):
    """Add custom header to pytest report."""
    return [
        "Document Processing Test Suite",
        "=" * 40,
        f"Test data directory: {test_config.get_config('test_data_dir')}",
        f"Temporary directory: {test_config.get_config('temp_dir')}",
        f"Coverage threshold: {test_config.get_config('coverage_threshold')}%",
        f"Performance timeout: {test_config.get_config('performance_timeout')}s",
        f"Memory limit: {test_config.get_config('memory_limit_mb')}MB",
        f"Max file size: {test_config.get_config('max_file_size_mb')}MB",
        f"Supported file types: {', '.join(test_config.get_config('supported_file_types'))}",
        f"Test disciplines: {', '.join(test_config.get_config('test_disciplines'))}",
        f"Test analysis modes: {', '.join(test_config.get_config('test_analysis_modes'))}",
        f"Test strictness levels: {', '.join(test_config.get_config('test_strictness_levels'))}",
        "=" * 40,
    ]


def pytest_report_teststatus(report, config):
    """Custom test status reporting."""
    if report.when == "call":
        if report.outcome == "passed":
            return "passed", "PASS", "green"
        elif report.outcome == "failed":
            return "failed", "FAIL", "red"
        elif report.outcome == "skipped":
            return "skipped", "SKIP", "yellow"
    return None


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Custom terminal summary."""
    terminalreporter.write_sep("=", "Document Processing Test Suite Summary")

    # Test results summary
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))
    total = passed + failed + skipped

    terminalreporter.write(f"Total tests: {total}\n")
    terminalreporter.write(f"Passed: {passed}\n")
    terminalreporter.write(f"Failed: {failed}\n")
    terminalreporter.write(f"Skipped: {skipped}\n")

    if total > 0:
        success_rate = (passed / total) * 100
        terminalreporter.write(f"Success rate: {success_rate:.1f}%\n")

    # Recommendations
    terminalreporter.write_sep("-", "Recommendations")

    if failed > 0:
        terminalreporter.write("* Review failed tests and fix issues\n")

    if success_rate < 90:
        terminalreporter.write("* Improve test reliability\n")

    terminalreporter.write("* Run tests regularly to catch regressions\n")
    terminalreporter.write("* Monitor performance metrics for degradation\n")
    terminalreporter.write("* Update tests when adding new features\n")

    terminalreporter.write_sep("=", "End of Summary")
