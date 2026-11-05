from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .auth.models import AuthSession
from .auth.service import auth_service
from .database.core import get_db
from .sensors.models import Sensor
from .sensors.service import sensor_service
from .users.models import User

# auto_error=False: a missing token gets a 401 from get_current_session, not a 403.
bearer_scheme = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]
Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
ApiKey = Annotated[str | None, Depends(api_key_scheme)]


def get_current_session(credentials: Credentials, db: DbSession) -> AuthSession:
    session = (
        auth_service.get_session(db, credentials.credentials) if credentials else None
    )
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return session


CurrentSession = Annotated[AuthSession, Depends(get_current_session)]


def get_current_user(session: CurrentSession) -> User:
    return session.user


CurrentUser = Annotated[User, Depends(get_current_user)]

# For routes that need a signed-in user but don't use it: dependencies=[login_required]
login_required = Depends(get_current_user)


def get_current_sensor(api_key: ApiKey, db: DbSession) -> Sensor:
    """The sensor (IoT device) identified by its X-API-Key header."""
    sensor = sensor_service.get_sensor_by_api_key(db, api_key) if api_key else None
    if sensor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    return sensor


CurrentSensor = Annotated[Sensor, Depends(get_current_sensor)]
