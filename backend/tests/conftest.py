import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.main import app
from app.users.schemas import UserCreate
from app.users.service import user_service


@pytest.fixture
def admin_client(db_session: Session) -> TestClient:
    """A TestClient signed in as a user (every signed-in user is an admin)."""
    password = "adminclientpassword"
    user_service.create_user(
        db_session, UserCreate(username="adminclient", password=password)
    )
    client = TestClient(app)
    response = client.post(
        f"{settings.AUTH_STR}/login",
        json={"username": "adminclient", "password": password},
    )
    client.headers["Authorization"] = f"Bearer {response.json()['accessToken']}"
    return client
