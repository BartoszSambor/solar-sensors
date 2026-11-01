import logging

from app.config import settings
from app.database.core import SessionFactory
from app.users.schemas import UserCreate
from app.users.service import user_service

logger = logging.getLogger(__name__)


def seed_db() -> None:
    """Create the first user from settings if it doesn't exist yet."""
    with SessionFactory() as db:
        username = settings.FIRST_SUPERUSER_USERNAME.lower()
        if user_service.get_user_by_username(db, username) is None:
            user_service.create_user(
                db,
                UserCreate(
                    username=username, password=settings.FIRST_SUPERUSER_PASSWORD
                ),
            )
            logger.info("First user created: %s", username)
        else:
            logger.info("User %s already exists.", username)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_db()
