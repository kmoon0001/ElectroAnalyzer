import uuid

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("httpx")

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_auth_register_login_change_password(client: AsyncClient, db_session: AsyncSession):
    # Unique username per test run
    username = f"int_user_{uuid.uuid4().hex[:8]}"
    password = "Str0ng!Passw0rd99"
    new_password = "Sup3r$afe!K9q7"

    # Register user
    r = await client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
            "is_admin": False,
        },
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["username"] == username

    # Login via JSON to obtain token
    r = await client.post(
        "/auth/json-login",
        json={"username": username, "password": password},
    )
    assert r.status_code == 200, r.text
    token = r.json().get("access_token")
    assert token and isinstance(token, str)

    # Change password using the token
    r = await client.put(
        "/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"old_password": password, "new_password": new_password},
    )
    assert r.status_code == 204, r.text

    # Login with new password to confirm change
    r = await client.post(
        "/auth/json-login",
        json={"username": username, "password": new_password},
    )
    assert r.status_code == 200, r.text
    assert r.json().get("access_token")
