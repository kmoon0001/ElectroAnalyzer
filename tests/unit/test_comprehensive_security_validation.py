"""Comprehensive validation and security tests for document processing.

This module provides thorough testing for:
- File validation and security checks
- Input sanitization and validation
- Security vulnerability detection
- Edge case handling
- Performance under security constraints
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from tests.data.test_documents import (
    create_malicious_file,
    create_oversized_file,
    create_corrupted_file,
    create_file_with_special_characters,
    create_file_with_unicode_content,
    create_file_with_mixed_encodings,
    create_file_with_empty_lines,
    create_file_with_very_long_lines,
    create_file_with_binary_content,
)


class TestFileValidationSecurity:
    """Comprehensive security tests for file validation."""

    def test_magic_number_validation_all_types(self):
        """Test magic number validation for all supported file types."""
        from src.core.file_upload_validator import FileMagicValidator

        # Test PDF validation
        pdf_content = b"%PDF-1.4\n%Sample PDF content"
        is_valid, error = FileMagicValidator.validate_file(pdf_content, "test.pdf")
        assert is_valid
        assert error is None

        # Test DOCX validation
        docx_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"
        is_valid, error = FileMagicValidator.validate_file(docx_content, "test.docx")
        assert is_valid
        assert error is None

        # Test TXT validation
        txt_content = b"Sample text content"
        is_valid, error = FileMagicValidator.validate_file(txt_content, "test.txt")
        assert is_valid
        assert error is None

    def test_file_size_validation_edge_cases(self):
        """Test file size validation with edge cases."""
        from src.core.file_upload_validator import FileMagicValidator

        # Empty file
        empty_content = b""
        is_valid, error = FileMagicValidator.validate_file(empty_content, "test.pdf")
        assert not is_valid
        assert "File is empty" in error

        # File at maximum size limit
        max_size_content = b"x" * (50 * 1024 * 1024)  # Exactly 50MB
        is_valid, error = FileMagicValidator.validate_file(max_size_content, "test.pdf")
        assert is_valid
        assert error is None

        # File exceeding maximum size
        oversized_content = b"x" * (51 * 1024 * 1024)  # 51MB
        is_valid, error = FileMagicValidator.validate_file(oversized_content, "test.pdf")
        assert not is_valid
        assert "File size exceeds maximum allowed size" in error

    def test_dangerous_pattern_detection_comprehensive(self):
        """Test comprehensive dangerous pattern detection."""
        from src.core.file_upload_validator import FileMagicValidator

        # Test all dangerous patterns
        dangerous_patterns = [
            ("script", "<script>alert('xss')</script>"),
            ("javascript", "javascript:alert('xss')"),
            ("iframe", "<iframe src='javascript:alert(\"xss\")'></iframe>"),
            ("object", "<object data='javascript:alert(\"xss\")'></object>"),
            ("embed", "<embed src='javascript:alert(\"xss\")'></embed>"),
            ("link", "<link rel='stylesheet' href='javascript:alert(\"xss\")'>"),
            ("meta", "<meta http-equiv='refresh' content='0;url=javascript:alert(\"xss\")'>"),
            ("style", "<style>body{background:url('javascript:alert(\"xss\")')}</style>"),
            ("expression", "<style>body{background:expression(alert('xss'))}</style>"),
            ("import", "@import url('javascript:alert(\"xss\")');"),
            ("data_html", "data:text/html,<script>alert('xss')</script>"),
            ("data_js", "data:application/javascript,alert('xss')"),
            ("blob", "blob:javascript:alert('xss')"),
            ("file", "file:///etc/passwd"),
            ("ftp", "ftp://malicious.com/file"),
            ("gopher", "gopher://malicious.com/"),
            ("jar", "jar:file:///malicious.jar!/"),
            ("ldap", "ldap://malicious.com/"),
            ("mailto", "mailto:malicious@evil.com"),
            ("tel", "tel:+1234567890"),
            ("telnet", "telnet://malicious.com/"),
            ("ws", "ws://malicious.com/"),
            ("wss", "wss://malicious.com/"),
        ]

        for pattern_type, content in dangerous_patterns:
            is_valid, error = FileMagicValidator.validate_file(content.encode(), "test.txt")
            assert not is_valid, f"Pattern {pattern_type} should be detected as dangerous"
            assert "Potentially dangerous content detected" in error

    def test_filename_security_validation(self):
        """Test filename security validation."""
        from src.core.security_validator import SecurityValidator

        # Valid filenames
        valid_filenames = [
            "document.pdf",
            "report.docx",
            "notes.txt",
            "file_123.pdf",
            "test-file.docx",
            "document.123.txt",
        ]

        for filename in valid_filenames:
            is_valid, error = SecurityValidator.validate_filename(filename)
            assert is_valid, f"Filename '{filename}' should be valid"
            assert error is None

        # Invalid filenames
        invalid_filenames = [
            "",  # Empty
            "x" * 300,  # Too long
            "../../../etc/passwd",  # Path traversal
            "..\\..\\..\\windows\\system32",  # Windows path traversal
            "file\x00name.pdf",  # Null byte
            "file\nname.pdf",  # Newline
            "file\rname.pdf",  # Carriage return
            "file\tname.pdf",  # Tab
            "file/name.pdf",  # Forward slash
            "file\\name.pdf",  # Backslash
            "file:name.pdf",  # Colon
            "file*name.pdf",  # Asterisk
            "file?name.pdf",  # Question mark
            "file\"name.pdf",  # Quote
            "file<name.pdf",  # Less than
            "file>name.pdf",  # Greater than
            "file|name.pdf",  # Pipe
        ]

        for filename in invalid_filenames:
            is_valid, error = SecurityValidator.validate_filename(filename)
            assert not is_valid, f"Filename '{filename}' should be invalid"
            assert error is not None

    def test_discipline_validation_comprehensive(self):
        """Test comprehensive discipline validation."""
        from src.core.security_validator import SecurityValidator

        # Valid disciplines
        valid_disciplines = ["pt", "ot", "slp"]

        for discipline in valid_disciplines:
            is_valid, error = SecurityValidator.validate_discipline(discipline)
            assert is_valid, f"Discipline '{discipline}' should be valid"
            assert error is None

        # Invalid disciplines
        invalid_disciplines = [
            "invalid",
            "PT",  # Wrong case
            "physical therapy",  # Full name
            "123",
            "",
            "pt; DROP TABLE users;",  # SQL injection attempt
            "pt<script>alert('xss')</script>",  # XSS attempt
            "pt' OR '1'='1",  # SQL injection attempt
        ]

        for discipline in invalid_disciplines:
            is_valid, error = SecurityValidator.validate_discipline(discipline)
            assert not is_valid, f"Discipline '{discipline}' should be invalid"
            assert error is not None

    def test_analysis_mode_validation_comprehensive(self):
        """Test comprehensive analysis mode validation."""
        from src.core.security_validator import SecurityValidator

        # Valid analysis modes
        valid_modes = ["rubric", "checklist", "hybrid"]

        for mode in valid_modes:
            is_valid, error = SecurityValidator.validate_analysis_mode(mode)
            assert is_valid, f"Analysis mode '{mode}' should be valid"
            assert error is None

        # Invalid analysis modes
        invalid_modes = [
            "invalid",
            "RUBRIC",  # Wrong case
            "123",
            "",
            "rubric; DROP TABLE users;",  # SQL injection attempt
            "rubric<script>alert('xss')</script>",  # XSS attempt
            "rubric' OR '1'='1",  # SQL injection attempt
        ]

        for mode in invalid_modes:
            is_valid, error = SecurityValidator.validate_analysis_mode(mode)
            assert not is_valid, f"Analysis mode '{mode}' should be invalid"
            assert error is not None

    def test_strictness_validation_comprehensive(self):
        """Test comprehensive strictness level validation."""
        from src.core.security_validator import SecurityValidator

        # Valid strictness levels
        valid_strictness = ["standard", "ultra_fast", "balanced", "thorough", "clinical_grade"]

        for strictness in valid_strictness:
            is_valid, error = SecurityValidator.validate_strictness(strictness)
            assert is_valid, f"Strictness '{strictness}' should be valid"
            assert error is None

        # Invalid strictness levels
        invalid_strictness = [
            "invalid",
            "STANDARD",  # Wrong case
            "123",
            "",
            "standard; DROP TABLE users;",  # SQL injection attempt
            "standard<script>alert('xss')</script>",  # XSS attempt
            "standard' OR '1'='1",  # SQL injection attempt
        ]

        for strictness in invalid_strictness:
            is_valid, error = SecurityValidator.validate_strictness(strictness)
            assert not is_valid, f"Strictness '{strictness}' should be invalid"
            assert error is not None

    def test_text_input_validation_comprehensive(self):
        """Test comprehensive text input validation."""
        from src.core.security_validator import SecurityValidator

        # Valid text inputs
        valid_inputs = [
            "Normal text content",
            "Text with numbers 123",
            "Text with symbols !@#$%^&*()",
            "Text with unicode: àáâãäåæçèéêë",
            "Text with emoji: 😀😁😂",
        ]

        for text_input in valid_inputs:
            is_valid, error = SecurityValidator.validate_text_input(text_input)
            assert is_valid, f"Text input should be valid"
            assert error is None

        # Invalid text inputs
        invalid_inputs = [
            "x" * 10001,  # Too long
            "<script>alert('xss')</script>",  # Script tag
            "javascript:alert('xss')",  # JavaScript protocol
            "onerror=alert('xss')",  # Event handler
            "onload=alert('xss')",  # Event handler
            "onclick=alert('xss')",  # Event handler
            "onmouseover=alert('xss')",  # Event handler
            "onfocus=alert('xss')",  # Event handler
            "onblur=alert('xss')",  # Event handler
            "onchange=alert('xss')",  # Event handler
            "onsubmit=alert('xss')",  # Event handler
            "onreset=alert('xss')",  # Event handler
            "onkeydown=alert('xss')",  # Event handler
            "onkeyup=alert('xss')",  # Event handler
            "onkeypress=alert('xss')",  # Event handler
            "../../../etc/passwd",  # Path traversal
            "..\\..\\..\\windows\\system32",  # Windows path traversal
            "<iframe src='javascript:alert(\"xss\")'></iframe>",  # Iframe injection
            "<object data='javascript:alert(\"xss\")'></object>",  # Object injection
            "<embed src='javascript:alert(\"xss\")'></embed>",  # Embed injection
            "<link rel='stylesheet' href='javascript:alert(\"xss\")'>",  # Link injection
            "<meta http-equiv='refresh' content='0;url=javascript:alert(\"xss\")'>",  # Meta injection
            "<style>body{background:url('javascript:alert(\"xss\")')}</style>",  # Style injection
            "expression(alert('xss'))",  # CSS expression
            "url(javascript:alert('xss'))",  # CSS url
            "@import url('javascript:alert(\"xss\")');",  # CSS import
            "vbscript:alert('xss')",  # VBScript protocol
            "data:text/html,<script>alert('xss')</script>",  # Data URI HTML
            "data:application/javascript,alert('xss')",  # Data URI JS
            "blob:javascript:alert('xss')",  # Blob URL
            "file:///etc/passwd",  # File protocol
            "ftp://malicious.com/file",  # FTP protocol
            "gopher://malicious.com/",  # Gopher protocol
            "jar:file:///malicious.jar!/",  # JAR protocol
            "ldap://malicious.com/",  # LDAP protocol
            "ldaps://malicious.com/",  # LDAPS protocol
            "mailto:malicious@evil.com",  # Mailto protocol
            "news://malicious.com/",  # News protocol
            "nntp://malicious.com/",  # NNTP protocol
            "tel:+1234567890",  # Tel protocol
            "telnet://malicious.com/",  # Telnet protocol
            "tftp://malicious.com/",  # TFTP protocol
            "ws://malicious.com/",  # WebSocket protocol
            "wss://malicious.com/",  # Secure WebSocket protocol
        ]

        for text_input in invalid_inputs:
            is_valid, error = SecurityValidator.validate_text_input(text_input)
            assert not is_valid, f"Text input should be invalid: {text_input[:50]}..."
            assert error is not None

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention in all validation methods."""
        from src.core.security_validator import SecurityValidator

        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' OR 1=1 --",
            "'; UPDATE users SET password='hacked' WHERE username='admin'; --",
            "' OR 'x'='x",
            "'; DELETE FROM users; --",
        ]

        for attempt in sql_injection_attempts:
            # Test filename validation
            is_valid, error = SecurityValidator.validate_filename(f"file{attempt}.pdf")
            assert not is_valid, f"SQL injection attempt should be detected in filename: {attempt}"
            assert error is not None

            # Test discipline validation
            is_valid, error = SecurityValidator.validate_discipline(f"pt{attempt}")
            assert not is_valid, f"SQL injection attempt should be detected in discipline: {attempt}"
            assert error is not None

            # Test analysis mode validation
            is_valid, error = SecurityValidator.validate_analysis_mode(f"rubric{attempt}")
            assert not is_valid, f"SQL injection attempt should be detected in analysis mode: {attempt}"
            assert error is not None

            # Test strictness validation
            is_valid, error = SecurityValidator.validate_strictness(f"standard{attempt}")
            assert not is_valid, f"SQL injection attempt should be detected in strictness: {attempt}"
            assert error is not None

            # Test text input validation
            is_valid, error = SecurityValidator.validate_text_input(f"content{attempt}")
            assert not is_valid, f"SQL injection attempt should be detected in text input: {attempt}"
            assert error is not None

    def test_xss_prevention(self):
        """Test XSS prevention in all validation methods."""
        from src.core.security_validator import SecurityValidator

        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onerror=alert('xss')",
            "onload=alert('xss')",
            "onclick=alert('xss')",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "<object data='javascript:alert(\"xss\")'></object>",
            "<embed src='javascript:alert(\"xss\")'></embed>",
            "<link rel='stylesheet' href='javascript:alert(\"xss\")'>",
            "<meta http-equiv='refresh' content='0;url=javascript:alert(\"xss\")'>",
            "<style>body{background:url('javascript:alert(\"xss\")')}</style>",
            "expression(alert('xss'))",
            "url(javascript:alert('xss'))",
            "@import url('javascript:alert(\"xss\")');",
            "vbscript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "data:application/javascript,alert('xss')",
            "blob:javascript:alert('xss')",
        ]

        for attempt in xss_attempts:
            # Test filename validation
            is_valid, error = SecurityValidator.validate_filename(f"file{attempt}.pdf")
            assert not is_valid, f"XSS attempt should be detected in filename: {attempt}"
            assert error is not None

            # Test text input validation
            is_valid, error = SecurityValidator.validate_text_input(f"content{attempt}")
            assert not is_valid, f"XSS attempt should be detected in text input: {attempt}"
            assert error is not None

    def test_path_traversal_prevention(self):
        """Test path traversal prevention in filename validation."""
        from src.core.security_validator import SecurityValidator

        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
        ]

        for attempt in path_traversal_attempts:
            is_valid, error = SecurityValidator.validate_filename(attempt)
            assert not is_valid, f"Path traversal attempt should be detected: {attempt}"
            assert error is not None

    def test_unicode_normalization_attacks(self):
        """Test Unicode normalization attack prevention."""
        from src.core.security_validator import SecurityValidator

        unicode_attack_attempts = [
            "file\u0000name.pdf",  # Null byte
            "file\u0001name.pdf",  # Control character
            "file\u0002name.pdf",  # Control character
            "file\u0003name.pdf",  # Control character
            "file\u0004name.pdf",  # Control character
            "file\u0005name.pdf",  # Control character
            "file\u0006name.pdf",  # Control character
            "file\u0007name.pdf",  # Control character
            "file\u0008name.pdf",  # Backspace
            "file\u0009name.pdf",  # Tab
            "file\u000aname.pdf",  # Newline
            "file\u000bname.pdf",  # Vertical tab
            "file\u000cname.pdf",  # Form feed
            "file\u000dname.pdf",  # Carriage return
            "file\u000ename.pdf",  # Shift out
            "file\u000fname.pdf",  # Shift in
            "file\u0010name.pdf",  # Data link escape
            "file\u0011name.pdf",  # Device control 1
            "file\u0012name.pdf",  # Device control 2
            "file\u0013name.pdf",  # Device control 3
            "file\u0014name.pdf",  # Device control 4
            "file\u0015name.pdf",  # Negative acknowledge
            "file\u0016name.pdf",  # Synchronous idle
            "file\u0017name.pdf",  # End of transmission block
            "file\u0018name.pdf",  # Cancel
            "file\u0019name.pdf",  # End of medium
            "file\u001aname.pdf",  # Substitute
            "file\u001bname.pdf",  # Escape
            "file\u001cname.pdf",  # File separator
            "file\u001dname.pdf",  # Group separator
            "file\u001ename.pdf",  # Record separator
            "file\u001fname.pdf",  # Unit separator
        ]

        for attempt in unicode_attack_attempts:
            is_valid, error = SecurityValidator.validate_filename(attempt)
            assert not is_valid, f"Unicode attack attempt should be detected: {attempt}"
            assert error is not None

    def test_encoding_attack_prevention(self):
        """Test encoding attack prevention."""
        from src.core.security_validator import SecurityValidator

        encoding_attack_attempts = [
            "file%00name.pdf",  # URL encoded null byte
            "file%01name.pdf",  # URL encoded control character
            "file%02name.pdf",  # URL encoded control character
            "file%03name.pdf",  # URL encoded control character
            "file%04name.pdf",  # URL encoded control character
            "file%05name.pdf",  # URL encoded control character
            "file%06name.pdf",  # URL encoded control character
            "file%07name.pdf",  # URL encoded control character
            "file%08name.pdf",  # URL encoded backspace
            "file%09name.pdf",  # URL encoded tab
            "file%0aname.pdf",  # URL encoded newline
            "file%0bname.pdf",  # URL encoded vertical tab
            "file%0cname.pdf",  # URL encoded form feed
            "file%0dname.pdf",  # URL encoded carriage return
            "file%0ename.pdf",  # URL encoded shift out
            "file%0fname.pdf",  # URL encoded shift in
            "file%10name.pdf",  # URL encoded data link escape
            "file%11name.pdf",  # URL encoded device control 1
            "file%12name.pdf",  # URL encoded device control 2
            "file%13name.pdf",  # URL encoded device control 3
            "file%14name.pdf",  # URL encoded device control 4
            "file%15name.pdf",  # URL encoded negative acknowledge
            "file%16name.pdf",  # URL encoded synchronous idle
            "file%17name.pdf",  # URL encoded end of transmission block
            "file%18name.pdf",  # URL encoded cancel
            "file%19name.pdf",  # URL encoded end of medium
            "file%1aname.pdf",  # URL encoded substitute
            "file%1bname.pdf",  # URL encoded escape
            "file%1cname.pdf",  # URL encoded file separator
            "file%1dname.pdf",  # URL encoded group separator
            "file%1ename.pdf",  # URL encoded record separator
            "file%1fname.pdf",  # URL encoded unit separator
        ]

        for attempt in encoding_attack_attempts:
            is_valid, error = SecurityValidator.validate_filename(attempt)
            assert not is_valid, f"Encoding attack attempt should be detected: {attempt}"
            assert error is not None

    def test_performance_under_security_constraints(self):
        """Test performance under security constraints."""
        import time
        from src.core.security_validator import SecurityValidator

        # Test with large inputs
        large_input = "x" * 10000

        start_time = time.time()
        is_valid, error = SecurityValidator.validate_text_input(large_input)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should process within reasonable time (1 second)
        assert processing_time < 1.0
        assert is_valid
        assert error is None

        # Test with many dangerous patterns
        dangerous_input = "<script>alert('xss')</script>" * 1000

        start_time = time.time()
        is_valid, error = SecurityValidator.validate_text_input(dangerous_input)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should process within reasonable time (1 second)
        assert processing_time < 1.0
        assert not is_valid
        assert error is not None

    def test_concurrent_security_validation(self):
        """Test concurrent security validation."""
        import threading
        import time
        from src.core.security_validator import SecurityValidator

        results = []
        errors = []

        def validate_security():
            try:
                # Test filename validation
                is_valid, error = SecurityValidator.validate_filename("test.pdf")
                results.append(("filename", is_valid, error))

                # Test discipline validation
                is_valid, error = SecurityValidator.validate_discipline("pt")
                results.append(("discipline", is_valid, error))

                # Test analysis mode validation
                is_valid, error = SecurityValidator.validate_analysis_mode("rubric")
                results.append(("analysis_mode", is_valid, error))

                # Test strictness validation
                is_valid, error = SecurityValidator.validate_strictness("standard")
                results.append(("strictness", is_valid, error))

                # Test text input validation
                is_valid, error = SecurityValidator.validate_text_input("test content")
                results.append(("text_input", is_valid, error))

            except Exception as e:
                errors.append(e)

        # Create multiple threads for concurrent validation
        threads = []
        for i in range(5):
            thread = threading.Thread(target=validate_security)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5)

        # Verify results
        assert len(results) == 25  # 5 threads * 5 validations each
        assert len(errors) == 0

        # Verify all results are valid
        for validation_type, is_valid, error in results:
            assert is_valid, f"Validation {validation_type} should be valid"
            assert error is None
