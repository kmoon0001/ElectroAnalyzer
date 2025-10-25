import pytest

pytest.importorskip("sqlalchemy")

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import crud, schemas
from src.auth import AuthService
from unittest.mock import patch


@pytest.mark.asyncio
async def test_update_current_user_password(client_with_auth_override: AsyncClient, db_session: AsyncSession):
    # The client fixture already provides a dummy user with password "password"
    # The authentication is already handled by the fixture override

    # Update the password using the dummy user from the fixture
    password_data = {"old_password": "password", "new_password": "new_password"}

    # Update the password (the user is already authenticated via the fixture)
    response = await client_with_auth_override.put("/users/me/password", json=password_data)

    assert response.status_code == 204

    # Verify the password was changed by trying to log in with the new password
    login_data = {"username": "testuser", "password": "new_password"}
    response = await client_with_auth_override.post("/auth/login", data=login_data)
    assert response.status_code == 200
