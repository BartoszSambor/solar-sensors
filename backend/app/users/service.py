from sqlalchemy.orm import Query, Session

from ..auth.security import get_password_hash
from . import schemas as user_schemas
from .models import User


class UserService:
    def _query(self, db: Session) -> Query[User]:
        return db.query(User)

    def list_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: user_schemas.UserFilter | None = None,
        sort: user_schemas.UserSort | None = None,
    ) -> user_schemas.UserListResponse:
        query = self._query(db)

        if filters:
            if filters.username:
                query = query.filter(User.username.ilike(f"%{filters.username}%"))
            if filters.created_at_from is not None:
                query = query.filter(User.created_at >= filters.created_at_from)
            if filters.created_at_to is not None:
                query = query.filter(User.created_at <= filters.created_at_to)

        if sort:
            column = getattr(User, sort.field, User.id)
            query = query.order_by(
                column.desc() if sort.direction == "desc" else column.asc()
            )

        return user_schemas.UserListResponse(
            users=query.offset(skip).limit(limit).all(),
            total=query.count(),
            skip=skip,
            limit=limit,
        )

    def create_user(self, db: Session, user_in: user_schemas.UserCreate) -> User:
        user = User(
            **user_in.model_dump(exclude={"password"}),
            password_hash=get_password_hash(user_in.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_user_by_id(self, db: Session, user_id: int) -> User | None:
        return self._query(db).filter(User.id == user_id).first()

    def get_user_by_username(self, db: Session, username: str) -> User | None:
        return self._query(db).filter(User.username == username).first()

    def delete_user(self, db: Session, user: User) -> None:
        db.delete(user)
        db.commit()


user_service = UserService()
