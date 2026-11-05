from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..models import _utcnow
from ..users.models import User
from ..users.service import user_service
from . import security
from .models import AuthSession
from .schemas import PasswordChangeRequest


class AuthService:
    def authenticate_user(
        self, db: Session, username: str, password: str
    ) -> User | None:
        # Usernames are stored lowercase (see validate_username).
        user = user_service.get_user_by_username(db, username.strip().lower())
        if not user or not security.verify_password(password, user.password_hash):
            return None
        return user

    def create_session(self, db: Session, user: User) -> str:
        """Start a session and return its token (only the hash is stored)."""
        now = _utcnow()
        # Housekeeping: drop this user's expired sessions.
        db.execute(
            delete(AuthSession).where(
                AuthSession.user_id == user.id, AuthSession.expires_at <= now
            )
        )
        token = security.generate_token()
        db.add(
            AuthSession(
                token_hash=security.hash_token(token),
                user_id=user.id,
                expires_at=now + security.SESSION_LIFETIME,
            )
        )
        db.commit()
        return token

    def get_session(self, db: Session, token: str) -> AuthSession | None:
        """Return the session for a token, unless it is unknown or expired."""
        return db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == security.hash_token(token),
                AuthSession.expires_at > _utcnow(),
            )
        )

    def revoke_session(self, db: Session, session: AuthSession) -> None:
        db.delete(session)
        db.commit()

    def change_password(
        self,
        db: Session,
        session: AuthSession,
        password_in: PasswordChangeRequest,
    ) -> None:
        user = session.user
        if not security.verify_password(
            password_in.current_password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password",
            )
        user.password_hash = security.get_password_hash(password_in.new_password)
        # Log out everywhere else; the session that changed the password stays.
        db.execute(
            delete(AuthSession).where(
                AuthSession.user_id == user.id,
                AuthSession.token_hash != session.token_hash,
            )
        )
        db.commit()


auth_service = AuthService()
