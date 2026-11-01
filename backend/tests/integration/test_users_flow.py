from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.users.schemas import UserCreate
from app.users.service import user_service


def test_list_users(
    client: TestClient, other_user_token_headers: dict, db_session: Session
):
    """Test listing users."""
    # Create some users
    user_service.create_user(
        db_session,
        UserCreate(username="user1", password="password123"),
    )
    user_service.create_user(
        db_session,
        UserCreate(username="user2", password="password123"),
    )

    response = client.get(
        f"{settings.API_V1_STR}/users/", headers=other_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3  # other_user + user1 + user2
    assert len(data["users"]) >= 3
