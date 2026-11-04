import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.core import get_db
from app.main import app
from app.models import Base
from app.series.models import Series


@pytest.fixture(name="db_session")
def db_session_fixture():
    # In-memory DB shared by all connections (StaticPool) and gone after the test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    db = TestingSessionLocal()
    yield db
    db.close()
    app.dependency_overrides.clear()


@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    return TestClient(app)


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
