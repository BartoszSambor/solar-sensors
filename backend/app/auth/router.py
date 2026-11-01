from fastapi import APIRouter, HTTPException, status

from ..dependencies import CurrentSession, DbSession
from . import schemas, security
from .service import auth_service

router = APIRouter()


@router.post("/login", response_model=schemas.LoginResponse)
def login(credentials: schemas.LoginRequest, db: DbSession) -> schemas.LoginResponse:
    user = auth_service.authenticate_user(
        db, username=credentials.username, password=credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return schemas.LoginResponse(
        access_token=auth_service.create_session(db, user),
        expires_in=int(security.SESSION_LIFETIME.total_seconds()),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(session: CurrentSession, db: DbSession) -> None:
    auth_service.revoke_session(db, session)


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    password_in: schemas.PasswordChangeRequest,
    session: CurrentSession,
    db: DbSession,
) -> None:
    auth_service.change_password(db, session, password_in)
