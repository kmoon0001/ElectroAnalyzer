import pytest
import pytest_asyncio

try:  # pragma: no cover - dependency availability
    from httpx import AsyncClient, ASGITransport
except ModuleNotFoundError as exc:  # pragma: no cover - handled via skip logic
    HTTPX_IMPORT_ERROR = exc
    AsyncClient = ASGITransport = object  # type: ignore[assignment]
else:
    HTTPX_IMPORT_ERROR = None

try:  # pragma: no cover - dependency availability
    from sqlalchemy.ext.asyncio import AsyncSession
except ModuleNotFoundError as exc:  # pragma: no cover - handled via skip logic
    SQLALCHEMY_IMPORT_ERROR = exc
    AsyncSession = object  # type: ignore[assignment]
else:
    SQLALCHEMY_IMPORT_ERROR = None

try:  # pragma: no cover - dependency availability
    from src.api.dependencies import get_analysis_service
    from src.api.main import app
    from src.auth import get_current_active_user
    from src.database import get_async_db, models
except ModuleNotFoundError as exc:  # pragma: no cover - handled via skip logic
    API_IMPORT_ERROR = exc
    get_analysis_service = get_current_active_user = get_async_db = None  # type: ignore[assignment]
    app = None  # type: ignore[assignment]
    models = None  # type: ignore[assignment]
else:
    API_IMPORT_ERROR = None


@pytest_asyncio.fixture
async def client_with_auth_override(db_session: AsyncSession) -> AsyncClient:
    if SQLALCHEMY_IMPORT_ERROR is not None:
        pytest.skip(
            "SQLAlchemy is required for API database fixtures but is not installed in this environment.",
            allow_module_level=True,
        )
    if HTTPX_IMPORT_ERROR is not None:
        pytest.skip(
            "httpx is required for API client fixtures but is not installed in this environment.",
            allow_module_level=True,
        )
    if API_IMPORT_ERROR is not None:
        pytest.skip(
            "FastAPI dependencies are unavailable; API tests cannot run in this environment.",
            allow_module_level=True,
        )

    # Create a dummy user for authentication (use models.User, not schemas.User)
    from src.database import models
    from src.auth import AuthService
    from datetime import datetime, UTC

    # Create a database model user with hashed_password attribute
    # Use a valid bcrypt hash for "password"
    auth_service = AuthService()
    dummy_user = models.User(
        id=1,
        username="testuser",
        hashed_password=auth_service.get_password_hash("password"),  # Hash of "password"
        is_active=True,
        is_admin=True,  # Set to True for admin tests
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    def override_get_current_active_user():
        # Check if the request has a specific user override
        # This allows tests to override the user if needed
        return dummy_user

    async def override_get_async_db() -> AsyncSession:
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Create a test client without authentication override for authorization tests."""
    if SQLALCHEMY_IMPORT_ERROR is not None:
        pytest.skip(
            "SQLAlchemy is required for API database fixtures but is not installed in this environment.",
            allow_module_level=True,
        )
    if HTTPX_IMPORT_ERROR is not None:
        pytest.skip(
            "httpx is required for API client fixtures but is not installed in this environment.",
            allow_module_level=True,
        )
    if API_IMPORT_ERROR is not None:
        pytest.skip(
            "FastAPI dependencies are unavailable; API tests cannot run in this environment.",
            allow_module_level=True,
        )

    async def override_get_async_db() -> AsyncSession:
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_async_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
