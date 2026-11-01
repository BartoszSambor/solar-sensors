from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash, verify_password
from app.users.schemas import UserCreate, UserFilter
from app.users.service import user_service


def test_password_hashing():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)


def test_create_user(db_session: Session):
    user_in = UserCreate(
        username="newuser",
        password="newpassword",
    )
    user = user_service.create_user(db_session, user_in=user_in)
    assert user.username == "newuser"
    assert user.id is not None


def test_get_user(db_session: Session):
    user_in = UserCreate(username="testgetuser", password="password")
    user = user_service.create_user(db_session, user_in)

    get_user = user_service.get_user_by_id(db_session, user.id)
    assert get_user
    assert get_user.id == user.id
    assert get_user.username == user.username

    get_user_by_name = user_service.get_user_by_username(db_session, user.username)
    assert get_user_by_name
    assert get_user_by_name.id == user.id
    assert get_user_by_name.username == user.username


def test_list_users(db_session: Session):
    user_service.create_user(
        db_session,
        UserCreate(username="listuser1", password="password"),
    )
    user_service.create_user(
        db_session,
        UserCreate(username="listuser2", password="password"),
    )

    response = user_service.list_users(db_session)
    assert response.total >= 2

    user_filter = UserFilter(username="listuser1")
    response = user_service.list_users(db_session, filters=user_filter)
    assert response.total >= 1
    assert response.users[0].username == "listuser1"


def test_list_users_filter_by_created_at(db_session: Session):
    before_create = datetime.now(timezone.utc)
    user_service.create_user(
        db_session,
        UserCreate(username="dateuser1", password="password"),
    )
    after_create = datetime.now(timezone.utc)

    # Filter with created_at_from before creation -> should include the user
    user_filter = UserFilter(created_at_from=before_create)
    response = user_service.list_users(db_session, filters=user_filter)
    usernames = [u.username for u in response.users]
    assert "dateuser1" in usernames

    # Filter with created_at_to after creation -> should include the user
    user_filter = UserFilter(created_at_to=after_create)
    response = user_service.list_users(db_session, filters=user_filter)
    usernames = [u.username for u in response.users]
    assert "dateuser1" in usernames

    # Filter with created_at_from in the future -> should not include the user
    user_filter = UserFilter(created_at_from=after_create + timedelta(hours=1))
    response = user_service.list_users(db_session, filters=user_filter)
    usernames = [u.username for u in response.users]
    assert "dateuser1" not in usernames


def test_delete_user(db_session: Session):
    user_in = UserCreate(username="deleteuser", password="password")
    user = user_service.create_user(db_session, user_in)
    user_id = user.id
    user_service.delete_user(db_session, user=user)
    deleted_user = user_service.get_user_by_id(db_session, user_id)
    assert deleted_user is None


# --- Router Tests ---


def test_list_users_api(client: TestClient, db_session: Session):
    user_service.create_user(
        db_session,
        UserCreate(username="listuser_api", password="longenoughpassword"),
    )
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
