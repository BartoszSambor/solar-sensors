from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth.models import AuthSession
from app.auth.security import hash_session_token
from app.config import settings
from app.models import _utcnow
from app.users.models import User

LOGIN = {"username": "testuser", "password": "testpassword123"}


def _login(client: TestClient, login_data: dict = LOGIN) -> dict:
    response = client.post(f"{settings.AUTH_STR}/login", json=login_data)
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


def _is_authorized(client: TestClient, headers: dict) -> bool:
    # A password change with a wrong current password has no side effects:
    # 400 when the token is valid, 401 when it isn't.
    response = client.put(
        f"{settings.AUTH_STR}/password",
        headers=headers,
        json={"currentPassword": "wrong-password", "newPassword": "whatever123"},
    )
    return response.status_code != 401


def test_login(client: TestClient, test_user: User):
    """Test login and token generation."""
    login_data = {"username": test_user.username, "password": "testpassword123"}
    response = client.post(f"{settings.AUTH_STR}/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert data.keys() == {"accessToken", "tokenType", "expiresIn"}
    assert data["tokenType"] == "Bearer"
    assert data["expiresIn"] == 30 * 60

    headers = {"Authorization": f"Bearer {data['accessToken']}"}
    response = client.post(f"{settings.AUTH_STR}/logout", headers=headers)
    assert response.status_code == 204


def test_login_is_case_insensitive(client: TestClient, test_user: User):
    login_data = {"username": "TestUser", "password": "testpassword123"}
    response = client.post(f"{settings.AUTH_STR}/login", json=login_data)
    assert response.status_code == 200


def test_login_wrong_password(client: TestClient, test_user: User):
    login_data = {"username": test_user.username, "password": "wrongpassword"}
    response = client.post(f"{settings.AUTH_STR}/login", json=login_data)
    assert response.status_code == 401


def test_logout(client: TestClient, user_token_headers: dict):
    response = client.post(f"{settings.AUTH_STR}/logout", headers=user_token_headers)
    assert response.status_code == 204


def test_logout_requires_token(client: TestClient):
    response = client.post(f"{settings.AUTH_STR}/logout")
    assert response.status_code == 401


def test_change_password(client: TestClient, user_token_headers: dict):
    """Test updating the current user's password."""
    password_data = {
        "currentPassword": "testpassword123",
        "newPassword": "newpassword456",
    }
    response = client.put(
        f"{settings.AUTH_STR}/password", headers=user_token_headers, json=password_data
    )
    assert response.status_code == 204

    # Verify we can login with the new password
    login_data = {"username": "testuser", "password": "newpassword456"}
    login_response = client.post(f"{settings.AUTH_STR}/login", json=login_data)
    assert login_response.status_code == 200


def test_change_password_wrong_current(client: TestClient, user_token_headers: dict):
    password_data = {
        "currentPassword": "wrongpassword",
        "newPassword": "newpassword456",
    }
    response = client.put(
        f"{settings.AUTH_STR}/password", headers=user_token_headers, json=password_data
    )
    assert response.status_code == 400


def test_only_token_hash_is_stored(
    client: TestClient, db_session: Session, test_user: User
):
    response = client.post(f"{settings.AUTH_STR}/login", json=LOGIN)
    token = response.json()["accessToken"]
    hashes = db_session.scalars(select(AuthSession.token_hash)).all()
    assert hashes == [hash_session_token(token)]
    assert token not in hashes


def test_logout_revokes_token(client: TestClient, test_user: User):
    headers = _login(client)
    assert _is_authorized(client, headers)
    response = client.post(f"{settings.AUTH_STR}/logout", headers=headers)
    assert response.status_code == 204
    assert not _is_authorized(client, headers)
    # A second logout with the same token is rejected too.
    response = client.post(f"{settings.AUTH_STR}/logout", headers=headers)
    assert response.status_code == 401


def test_logout_keeps_other_sessions(client: TestClient, test_user: User):
    first, second = _login(client), _login(client)
    client.post(f"{settings.AUTH_STR}/logout", headers=first)
    assert _is_authorized(client, second)


def test_unknown_token_rejected(client: TestClient):
    assert not _is_authorized(client, {"Authorization": "Bearer not-a-real-token"})


def test_expired_token_rejected(
    client: TestClient, db_session: Session, test_user: User
):
    headers = _login(client)
    db_session.execute(
        update(AuthSession).values(expires_at=_utcnow() - timedelta(seconds=1))
    )
    assert not _is_authorized(client, headers)


def test_change_password_revokes_other_sessions(client: TestClient, test_user: User):
    current, other = _login(client), _login(client)
    response = client.put(
        f"{settings.AUTH_STR}/password",
        headers=current,
        json={"currentPassword": "testpassword123", "newPassword": "newpassword456"},
    )
    assert response.status_code == 204
    assert _is_authorized(client, current)
    assert not _is_authorized(client, other)
