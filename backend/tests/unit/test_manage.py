import pytest
from sqlalchemy.orm import Session

from app.manage import CommandError, create_user, delete_user
from app.users.service import user_service


def test_create_user(db_session: Session):
    create_user(db_session, "Admin", "strongpassword")

    assert user_service.get_user_by_username(db_session, "admin") is not None


def test_create_user_rejects_duplicate_username(db_session: Session):
    create_user(db_session, "admin", "strongpassword")

    with pytest.raises(CommandError, match="already exists"):
        create_user(db_session, "ADMIN", "strongpassword")


def test_create_user_rejects_short_password(db_session: Session):
    with pytest.raises(CommandError, match="password"):
        create_user(db_session, "admin", "short")


def test_delete_user(db_session: Session):
    create_user(db_session, "admin", "strongpassword")

    delete_user(db_session, "Admin")

    assert user_service.get_user_by_username(db_session, "admin") is None


def test_delete_missing_user(db_session: Session):
    with pytest.raises(CommandError, match="does not exist"):
        delete_user(db_session, "ghost")
