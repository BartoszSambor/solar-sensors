from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from testcontainers.community.postgres import PostgresContainer

from app.config import settings
from app.database.core import get_db
from app.main import app
from app.models import Base
from app.series.models import Series
from app.users.models import User
from app.users.schemas import UserCreate
from app.users.service import user_service

POSTGRES_IMAGE = "postgres:17"  # keep in sync with docker-compose.yml


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """Starts a throwaway Postgres container for the whole test session."""
    with PostgresContainer(POSTGRES_IMAGE, driver="psycopg") as postgres:
        engine = create_engine(postgres.get_connection_url(), poolclass=StaticPool)
        Base.metadata.create_all(bind=engine)
        yield engine
        engine.dispose()


@pytest.fixture
def db_session(engine: Engine):
    """Provides a transactional database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, autoflush=False)

    # Override the get_db dependency to use this session
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture
def client(db_session: Session):
    """Provides a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Creates a regular test user."""
    user_in = UserCreate(
        username="testuser",
        password="testpassword123",
    )
    return user_service.create_user(db_session, user_in=user_in)


@pytest.fixture
def other_user(db_session: Session) -> User:
    """Creates a other_user for testing."""
    user_in = UserCreate(
        username="testadmin",
        password="adminpassword123",
    )
    return user_service.create_user(db_session, user_in=user_in)


@pytest.fixture
def user_token_headers(client: TestClient, test_user: User):
    """Provides authentication headers for a regular user."""
    login_data = {
        "username": test_user.username,
        "password": "testpassword123",
    }
    r = client.post(f"{settings.AUTH_STR}/login", json=login_data)
    tokens = r.json()
    a_token = tokens["accessToken"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture
def other_user_token_headers(client: TestClient, other_user: User):
    """Provides authentication headers for a other_user."""
    login_data = {
        "username": other_user.username,
        "password": "adminpassword123",
    }
    r = client.post(f"{settings.AUTH_STR}/login", json=login_data)
    tokens = r.json()
    a_token = tokens["accessToken"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture
def series(db_session: Session) -> Series:
    series = Series(
        name="Temperature",
        min_value=-40,
        max_value=85,
        color="#d62728",
        icon="thermostat",
        unit="°C",
    )
    db_session.add(series)
    db_session.commit()
    return series
