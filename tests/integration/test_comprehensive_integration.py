"""Comprehensive Integration Test Suite

Tests complete workflows and system integration:
- End-to-end document analysis workflow
- Authentication and authorization flows
- Database integration
- AI model integration
- Error handling and recovery
- Cross-component communication
"""

import pytest
import asyncio
import aiohttp
import requests
import time
from typing import Dict, Any, Optional
from pathlib import Path
import json
import tempfile
import os

class IntegrationTestBase:
    """Base class for integration tests."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session = requests.Session()

    async def authenticate(self) -> bool:
        """Authenticate and get token."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/auth/login",
                    json={"username": "admin", "password": "admin123"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.token = data["access_token"]
                        return True
            return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def create_test_document(self, content: str = "Patient presents with acute back pain. Assessment shows limited ROM. Plan includes PT exercises.") -> str:
        """Create a test document file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            return f.name

    def cleanup_test_file(self, file_path: str):
        """Clean up test file."""
        try:
            os.unlink(file_path)
        except Exception:
            pass

class TestCompleteWorkflow(IntegrationTestBase):
    """Test complete document analysis workflow."""

    @pytest.mark.asyncio
    async def test_complete_document_analysis_workflow(self):
        """Test complete document analysis workflow from upload to results."""
        # 1. Authenticate
        assert await self.authenticate(), "Authentication failed"

        # 2. Create test document
        test_file = self.create_test_document()

        try:
            # 3. Upload and analyze document
            headers = {"Authorization": f"Bearer {self.token}"}

            with open(test_file, 'rb') as f:
                files = {"file": f}
                data = {"discipline": "PT", "analysis_mode": "rubric"}

                response = requests.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    data=data,
                    headers=headers
                )

            assert response.status_code == 202, f"Upload failed: {response.text}"
            result = response.json()
            task_id = result["task_id"]

            # 4. Wait for analysis completion
            max_wait = 60  # 60 seconds
            wait_time = 0

            while wait_time < max_wait:
                response = requests.get(
                    f"{self.base_url}/analysis/{task_id}",
                    headers=headers
                )

                assert response.status_code == 200, f"Status check failed: {response.text}"
                data = response.json()

                if data["status"] == "completed":
                    # 5. Verify results
                    assert "compliance_score" in data
                    assert "findings" in data
                    assert isinstance(data["compliance_score"], (int, float))
                    assert isinstance(data["findings"], list)

                    print(f"Analysis completed - Score: {data['compliance_score']}")
                    return

                elif data["status"] == "failed":
                    pytest.fail(f"Analysis failed: {data.get('error', 'Unknown error')}")

                time.sleep(2)
                wait_time += 2

            pytest.fail("Analysis timed out")

        finally:
            self.cleanup_test_file(test_file)

    @pytest.mark.asyncio
    async def test_multiple_document_workflow(self):
        """Test workflow with multiple documents."""
        assert await self.authenticate(), "Authentication failed"

        # Create multiple test documents
        test_files = []
        for i in range(3):
            content = f"Patient {i+1} presents with condition. Assessment shows progress. Plan includes treatment."
            test_file = self.create_test_document(content)
            test_files.append(test_file)

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            task_ids = []

            # Upload all documents
            for test_file in test_files:
                with open(test_file, 'rb') as f:
                    files = {"file": f}
                    data = {"discipline": "PT"}

                    response = requests.post(
                        f"{self.base_url}/analyze",
                        files=files,
                        data=data,
                        headers=headers
                    )

                assert response.status_code == 202
                result = response.json()
                task_ids.append(result["task_id"])

            # Wait for all analyses to complete
            completed_count = 0
            max_wait = 120  # 2 minutes for multiple documents
            wait_time = 0

            while wait_time < max_wait and completed_count < len(task_ids):
                completed_count = 0

                for task_id in task_ids:
                    response = requests.get(
                        f"{self.base_url}/analysis/{task_id}",
                        headers=headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data["status"] == "completed":
                            completed_count += 1
                        elif data["status"] == "failed":
                            pytest.fail(f"Analysis {task_id} failed")

                if completed_count == len(task_ids):
                    print(f"All {len(task_ids)} analyses completed successfully")
                    return

                time.sleep(3)
                wait_time += 3

            pytest.fail(f"Only {completed_count}/{len(task_ids)} analyses completed")

        finally:
            for test_file in test_files:
                self.cleanup_test_file(test_file)

class TestAuthenticationIntegration(IntegrationTestBase):
    """Test authentication and authorization integration."""

    @pytest.mark.asyncio
    async def test_authentication_flow(self):
        """Test complete authentication flow."""
        # 1. Test login
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/auth/login",
                json={"username": "admin", "password": "admin123"}
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "access_token" in data
                assert "token_type" in data
                token = data["access_token"]

        # 2. Test protected endpoint access
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.base_url}/analysis/status", headers=headers)
        assert response.status_code == 200

        # 3. Test invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{self.base_url}/analysis/status", headers=invalid_headers)
        assert response.status_code == 401

        # 4. Test missing token
        response = requests.get(f"{self.base_url}/analysis/status")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_user_registration_flow(self):
        """Test user registration flow."""
        # 1. Register new user
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/auth/register",
                json={
                    "username": "testuser_integration",
                    "password": "testpassword123",
                    "is_admin": False
                }
            ) as response:
                assert response.status == 201
                data = await response.json()
                assert "username" in data

        # 2. Login with new user
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/auth/login",
                json={"username": "testuser_integration", "password": "testpassword123"}
            ) as response:
                assert response.status == 200
                data = await response.json()
                token = data["access_token"]

        # 3. Test access with new user
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.base_url}/analysis/status", headers=headers)
        assert response.status_code == 200

class TestDatabaseIntegration(IntegrationTestBase):
    """Test database integration."""

    @pytest.mark.asyncio
    async def test_database_persistence(self):
        """Test that data persists correctly in database."""
        assert await self.authenticate(), "Authentication failed"

        # 1. Create analysis
        test_file = self.create_test_document()

        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            with open(test_file, 'rb') as f:
                files = {"file": f}
                data = {"discipline": "PT"}

                response = requests.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    data=data,
                    headers=headers
                )

            assert response.status_code == 202
            result = response.json()
            task_id = result["task_id"]

            # 2. Wait for completion
            max_wait = 60
            wait_time = 0

            while wait_time < max_wait:
                response = requests.get(
                    f"{self.base_url}/analysis/{task_id}",
                    headers=headers
                )

                data = response.json()
                if data["status"] == "completed":
                    break
                elif data["status"] == "failed":
                    pytest.fail("Analysis failed")

                time.sleep(2)
                wait_time += 2

            # 3. Verify data persistence by restarting and checking again
            # (This would require API restart capability)
            response = requests.get(
                f"{self.base_url}/analysis/{task_id}",
                headers=headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert "compliance_score" in data

        finally:
            self.cleanup_test_file(test_file)

    @pytest.mark.asyncio
    async def test_database_concurrent_access(self):
        """Test database handles concurrent access correctly."""
        assert await self.authenticate(), "Authentication failed"

        # Create multiple concurrent requests
        async def create_analysis(session, i):
            test_file = self.create_test_document(f"Document {i} content for testing.")

            try:
                headers = {"Authorization": f"Bearer {self.token}"}

                with open(test_file, 'rb') as f:
                    files = {"file": f}
                    data = {"discipline": "PT"}

                    response = requests.post(
                        f"{self.base_url}/analyze",
                        files=files,
                        data=data,
                        headers=headers
                    )

                return response.json() if response.status_code == 202 else None

            finally:
                self.cleanup_test_file(test_file)

        # Make 5 concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = [create_analysis(session, i) for i in range(5)]
            results = await asyncio.gather(*tasks)

        # All requests should succeed
        successful_results = [r for r in results if r is not None]
        assert len(successful_results) == 5, f"Only {len(successful_results)}/5 requests succeeded"

class TestErrorHandlingIntegration(IntegrationTestBase):
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_invalid_file_handling(self):
        """Test handling of invalid files."""
        assert await self.authenticate(), "Authentication failed"

        # Create invalid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.invalid', delete=False) as f:
            f.write("This is not a valid document format")
            invalid_file = f.name

        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            with open(invalid_file, 'rb') as f:
                files = {"file": f}
                data = {"discipline": "PT"}

                response = requests.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    data=data,
                    headers=headers
                )

            # Should handle invalid file gracefully
            assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

            error_data = response.json()
            assert "error" in error_data or "detail" in error_data

        finally:
            self.cleanup_test_file(invalid_file)

    @pytest.mark.asyncio
    async def test_oversized_file_handling(self):
        """Test handling of oversized files."""
        assert await self.authenticate(), "Authentication failed"

        # Create oversized file (simulate)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Write large content
            large_content = "Patient data " * 10000  # ~130KB
            f.write(large_content)
            large_file = f.name

        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            with open(large_file, 'rb') as f:
                files = {"file": f}
                data = {"discipline": "PT"}

                response = requests.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    data=data,
                    headers=headers
                )

            # Should handle large file appropriately
            assert response.status_code in [200, 202, 413], f"Unexpected status: {response.status_code}"

        finally:
            self.cleanup_test_file(large_file)

    @pytest.mark.asyncio
    async def test_network_error_recovery(self):
        """Test recovery from network errors."""
        assert await self.authenticate(), "Authentication failed"

        # Test with invalid endpoint
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(
                f"{self.base_url}/nonexistent-endpoint",
                headers=headers,
                timeout=5
            )
            assert response.status_code == 404
        except requests.exceptions.RequestException:
            # Network errors should be handled gracefully
            pass

class TestCrossComponentIntegration(IntegrationTestBase):
    """Test integration between different components."""

    @pytest.mark.asyncio
    async def test_ai_model_integration(self):
        """Test AI model integration."""
        assert await self.authenticate(), "Authentication failed"

        # Check AI model status
        response = requests.get(f"{self.base_url}/ai/status")
        assert response.status_code == 200

        ai_status = response.json()
        print(f"AI Model Status: {ai_status}")

        # Test analysis with AI models
        test_file = self.create_test_document("Patient shows significant improvement in mobility and strength.")

        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            with open(test_file, 'rb') as f:
                files = {"file": f}
                data = {"discipline": "PT", "analysis_mode": "rubric"}

                response = requests.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    data=data,
                    headers=headers
                )

            assert response.status_code == 202
            result = response.json()
            task_id = result["task_id"]

            # Wait for AI analysis
            max_wait = 60
            wait_time = 0

            while wait_time < max_wait:
                response = requests.get(
                    f"{self.base_url}/analysis/{task_id}",
                    headers=headers
                )

                data = response.json()
                if data["status"] == "completed":
                    # Verify AI-generated results
                    assert "compliance_score" in data
                    assert "findings" in data
                    assert isinstance(data["compliance_score"], (int, float))
                    print(f"AI Analysis completed - Score: {data['compliance_score']}")
                    return
                elif data["status"] == "failed":
                    pytest.fail("AI analysis failed")

                time.sleep(2)
                wait_time += 2

            pytest.fail("AI analysis timed out")

        finally:
            self.cleanup_test_file(test_file)

    @pytest.mark.asyncio
    async def test_caching_integration(self):
        """Test caching system integration."""
        assert await self.authenticate(), "Authentication failed"

        # Test with identical documents (should use cache)
        test_content = "Identical test document for caching verification."
        test_file1 = self.create_test_document(test_content)
        test_file2 = self.create_test_document(test_content)

        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            # First analysis
            with open(test_file1, 'rb') as f:
                files = {"file": f}
                data = {"discipline": "PT"}

                response1 = requests.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    data=data,
                    headers=headers
                )

            assert response1.status_code == 202
            result1 = response1.json()
            task_id1 = result1["task_id"]

            # Second analysis (identical content)
            with open(test_file2, 'rb') as f:
                files = {"file": f}
                data = {"discipline": "PT"}

                response2 = requests.post(
                    f"{self.base_url}/analyze",
                    files=files,
                    data=data,
                    headers=headers
                )

            assert response2.status_code == 202
            result2 = response2.json()
            task_id2 = result2["task_id"]

            # Wait for both to complete
            for task_id in [task_id1, task_id2]:
                max_wait = 60
                wait_time = 0

                while wait_time < max_wait:
                    response = requests.get(
                        f"{self.base_url}/analysis/{task_id}",
                        headers=headers
                    )

                    data = response.json()
                    if data["status"] == "completed":
                        break
                    elif data["status"] == "failed":
                        pytest.fail(f"Analysis {task_id} failed")

                    time.sleep(2)
                    wait_time += 2

            # Verify both analyses completed
            response1 = requests.get(f"{self.base_url}/analysis/{task_id1}", headers=headers)
            response2 = requests.get(f"{self.base_url}/analysis/{task_id2}", headers=headers)

            assert response1.status_code == 200
            assert response2.status_code == 200

            data1 = response1.json()
            data2 = response2.json()

            # Results should be identical (cached)
            assert data1["compliance_score"] == data2["compliance_score"]
            print("Caching integration test passed")

        finally:
            self.cleanup_test_file(test_file1)
            self.cleanup_test_file(test_file2)

# Integration test configuration
@pytest.fixture(scope="session")
def integration_test_setup():
    """Setup for integration tests."""
    base = IntegrationTestBase()
    return base

# Test execution configuration
def pytest_configure(config):
    """Configure pytest for integration tests."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

# Integration test markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow
]
