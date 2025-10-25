"""
E2E Test Configuration and Fixtures

Provides shared fixtures and configuration for end-to-end testing.
"""

import asyncio
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

pytest.importorskip("sqlalchemy")

from fastapi.testclient import TestClient

# Import application components
from src.api.main import app
from src.config import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Test-specific settings configuration."""
    settings = get_settings()
    # Override settings for testing
    settings.database_url = "sqlite:///./test_e2e.db"
    settings.testing = True
    return settings


@pytest.fixture(scope="session")
def test_client(test_settings, test_db) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application with proper database isolation."""
    # Override the database dependency to use test database
    from src.database.database import get_async_db

    # Get the test session factory from test_db fixture
    TestAsyncSessionLocal = test_db.test_session_factory

    # Create a test-specific database dependency using the test database engine
    async def get_test_db():
        async with TestAsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    # Clear any existing overrides first
    app.dependency_overrides.clear()

    # Override the dependency BEFORE creating the TestClient
    app.dependency_overrides[get_async_db] = get_test_db

    # Load rubrics into the test database using the same session factory
    async def load_rubrics():
        async with TestAsyncSessionLocal() as session:
            from src.core.rubric_loader import parse_and_load_rubrics
            from pathlib import Path
            from src.database.models import ComplianceRubric
            from sqlalchemy import select

            # Check if rubrics are already loaded
            result = await session.execute(select(ComplianceRubric))
            existing_rubrics = result.scalars().all()

            if not existing_rubrics:
                # Find TTL files in the resources directory
                src_path = Path(__file__).parent.parent.parent
                rubrics_path = src_path / "src" / "resources" / "rubrics"
                ttl_files = list(rubrics_path.glob("*.ttl")) if rubrics_path.exists() else []

                print(f"Found {len(ttl_files)} TTL files in {rubrics_path}")

                if ttl_files:
                    await parse_and_load_rubrics(session, ttl_files)
                    await session.commit()

                    # Verify rubrics were loaded
                    result = await session.execute(select(ComplianceRubric))
                    loaded_rubrics = result.scalars().all()
                    print(f"Loaded {len(loaded_rubrics)} rubrics into test database")
                else:
                    # Fallback: create a simple test rubric manually
                    test_rubric = ComplianceRubric(
                        name="PT Compliance Test Rubric",
                        discipline="PT",
                        regulation="Standard PT compliance rubric for testing",
                        common_pitfalls="Missing subjective/objective data",
                        best_practice="Document all SOAP sections",
                        category="Test"
                    )
                    session.add(test_rubric)
                    await session.commit()
                    print("Created fallback test rubric")

    # Load rubrics synchronously
    import asyncio
    asyncio.run(load_rubrics())

    # Verify rubrics are accessible via the API
    print("Verifying rubrics are accessible via API...")
    test_client = TestClient(app)
    try:
        # Create a test user and get auth token
        register_data = {"username": "test_therapist", "password": "Th3r@p1sBetter", "is_admin": False}
        register_response = test_client.post("/auth/register", json=register_data)
        assert register_response.status_code == 201

        login_data = {"username": "test_therapist", "password": "Th3r@p1sBetter"}
        login_response = test_client.post("/auth/token", data=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Test rubrics endpoint
        headers = {"Authorization": f"Bearer {token}"}
        rubrics_response = test_client.get("/rubrics/", headers=headers)
        print(f"Rubrics API response: {rubrics_response.status_code}, {rubrics_response.text}")

        if rubrics_response.status_code == 200:
            rubrics_data = rubrics_response.json()
            print(f"Rubrics returned: {len(rubrics_data.get('rubrics', []))} rubrics")
    except Exception as e:
        print(f"Error verifying rubrics: {e}")
    finally:
        test_client.close()

    with TestClient(app) as client:
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
async def test_db(test_settings):
    """Create a test database for E2E testing."""
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from src.database import crud, schemas
    from src.database.database import Base

    # Create test-specific engine and session factory
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///./test_e2e.db",
        future=True,
        poolclass=NullPool,
        echo=False
    )

    TestAsyncSessionLocal = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False
    )

    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default rubrics so end-to-end workflows have options
    async with TestAsyncSessionLocal() as session:
        # Use the rubric loader to ensure proper loading
        from src.core.rubric_loader import parse_and_load_rubrics
        from pathlib import Path

        # Find TTL files in the resources directory
        src_path = Path(__file__).parent.parent.parent
        rubrics_path = src_path / "src" / "resources" / "rubrics"
        ttl_files = list(rubrics_path.glob("*.ttl")) if rubrics_path.exists() else []

        print(f"Found {len(ttl_files)} TTL files in {rubrics_path}")

        if ttl_files:
            await parse_and_load_rubrics(session, ttl_files)
            await session.commit()

            # Verify rubrics were loaded
            from src.database.models import ComplianceRubric
            from sqlalchemy import select
            result = await session.execute(select(ComplianceRubric))
            loaded_rubrics = result.scalars().all()
            print(f"Loaded {len(loaded_rubrics)} rubrics into test database")
        else:
            # Fallback: create a simple test rubric manually
            from src.database.models import ComplianceRubric
            test_rubric = ComplianceRubric(
                name="PT Compliance Test Rubric",
                discipline="PT",
                regulation="Standard PT compliance rubric for testing",
                common_pitfalls="Missing subjective/objective data",
                best_practice="Document all SOAP sections",
                category="Test"
            )
            session.add(test_rubric)
            await session.commit()
            print("Created fallback test rubric")

    # Store the test session factory for use in test_client
    test_db.test_session_factory = TestAsyncSessionLocal

    yield test_db

    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "username": "test_therapist",
        "email": "test@example.com",
        "password": "Th3r@p1sBetter",
        "is_admin": False,
    }


@pytest.fixture
def test_document_content():
    """Sample document content for testing."""
    return """
    PHYSICAL THERAPY PROGRESS NOTE

    Patient: John Doe (DOB: 01/01/1980)
    Date: 2024-01-15
    Therapist: Jane Smith, PT

    SUBJECTIVE:
    Patient reports decreased pain in lower back from 8/10 to 5/10 since last visit.
    States he is able to walk longer distances without significant discomfort.

    OBJECTIVE:
    Range of Motion: Lumbar flexion 45 degrees (improved from 30 degrees)
    Strength: Hip flexors 4/5, Hip extensors 4/5
    Functional: Able to sit to stand with minimal assistance

    ASSESSMENT:
    Patient demonstrates good progress with current treatment plan.
    Functional improvements noted in mobility and pain management.

    PLAN:
    Continue current exercise program
    Progress to more challenging strengthening exercises
    Patient education on home exercise program
    Next appointment in 1 week
    """


@pytest.fixture
def test_rubric_data():
    """Sample rubric data for testing."""
    return {
        "name": "PT Compliance Test Rubric",
        "discipline": "pt",
        "rules": [
            {
                "id": "subjective_required",
                "description": "Progress note must include subjective section",
                "pattern": r"SUBJECTIVE:",
                "severity": "high",
            },
            {
                "id": "objective_measurements",
                "description": "Objective section must include measurable data",
                "pattern": r"Range of Motion|Strength|Functional",
                "severity": "medium",
            },
            {
                "id": "assessment_present",
                "description": "Assessment section must be present",
                "pattern": r"ASSESSMENT:",
                "severity": "high",
            },
            {
                "id": "plan_documented",
                "description": "Plan section must be documented",
                "pattern": r"PLAN:",
                "severity": "high",
            },
        ],
    }


@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads."""
    temp_dir = tempfile.mkdtemp(prefix="e2e_test_uploads_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_document_file(temp_upload_dir, test_document_content):
    """Create a sample document file for testing."""
    doc_file = temp_upload_dir / "test_progress_note.txt"
    doc_file.write_text(test_document_content)
    return doc_file


@pytest.fixture
def mock_ai_services():
    """Mock AI services for faster testing."""
    mocks = {"llm_service": Mock(), "ner_service": Mock(), "embedding_service": Mock(), "compliance_analyzer": Mock()}

    # Configure mock responses
    mocks["llm_service"].generate_response.return_value = {
        "response": "This is a mock AI response for testing.",
        "confidence": 0.85,
    }

    mocks["compliance_analyzer"].analyze.return_value = {
        "findings": [
            {
                "id": "test_finding_1",
                "title": "Test Compliance Issue",
                "description": "This is a test compliance finding",
                "severity": "medium",
                "confidence": 0.8,
                "evidence": "Test evidence text",
            }
        ],
        "overall_score": 75,
        "document_type": "progress_note",
    }

    return mocks


@pytest.fixture
def authenticated_headers(test_client, test_user_data):
    """Get authentication headers for API requests."""
    # Create test user
    response = test_client.post("/auth/register", json=test_user_data)
    assert response.status_code in [200, 201, 409]  # 409 if user already exists

    # Login to get token
    login_data = {"username": test_user_data["username"], "password": test_user_data["password"]}
    response = test_client.post("/auth/token", data=login_data)
    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def e2e_test_config():
    """Configuration for E2E tests."""
    return {
        "api_base_url": "http://testserver",
        "timeout": 30,
        "max_retries": 3,
        "test_data_dir": Path(__file__).parent / "test_data",
        "performance_thresholds": {
            "document_analysis": 120,  # seconds
            "api_response": 5,  # seconds
            "pdf_export": 30,  # seconds
        },
    }


class E2ETestHelper:
    """Helper class for common E2E test operations."""

    def __init__(self, client: TestClient, headers: dict[str, str]):
        self.client = client
        self.headers = headers

    def upload_document(self, file_path: Path) -> dict[str, Any]:
        """Upload a document and return the response."""
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "text/plain")}
            response = self.client.post("/upload-document", files=files, headers=self.headers)
        return response.json()

    def start_analysis(self, document_id: str, rubric_id: str) -> dict[str, Any]:
        """Start document analysis and return task ID."""
        data = {"document_id": document_id, "rubric_id": rubric_id, "analysis_type": "comprehensive"}
        response = self.client.post("/analyze", json=data, headers=self.headers)
        return response.json()

    def wait_for_analysis(self, task_id: str, timeout: int = 120) -> dict[str, Any]:
        """Wait for analysis to complete and return results."""
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self.client.get(f"/analysis-status/{task_id}", headers=self.headers)
            result = response.json()

            if result.get("status") == "completed":
                return result
            elif result.get("status") == "failed":
                raise Exception(f"Analysis failed: {result.get('error')}")

            time.sleep(2)

        raise TimeoutError(f"Analysis did not complete within {timeout} seconds")


@pytest.fixture
def e2e_helper(test_client, authenticated_headers):
    """Create an E2E test helper instance."""
    return E2ETestHelper(test_client, authenticated_headers)
