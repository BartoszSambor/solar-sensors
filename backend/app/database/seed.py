import logging

from sqlalchemy import select

from app.config import settings
from app.database.core import SessionFactory
from app.series.models import Series
from app.users.schemas import UserCreate
from app.users.service import user_service

logger = logging.getLogger(__name__)

# There is no series API yet, so the series are seeded.
DEFAULT_SERIES = [
    {
        "name": "Temperature",
        "min_value": -40,
        "max_value": 85,
        "unit": "°C",
        "color": "#d62728",
        "icon": "thermostat",
    },
    {
        "name": "Irradiance",
        "min_value": 0,
        "max_value": 1500,
        "unit": "W/m²",
        "color": "#ff7f0e",
        "icon": "wb_sunny",
    },
    {
        "name": "Power",
        "min_value": 0,
        "max_value": 10000,
        "unit": "W",
        "color": "#1f77b4",
        "icon": "bolt",
    },
]


def seed_db() -> None:
    """Create the first user and the default series if they don't exist yet."""
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

        if db.execute(select(Series).limit(1)).first() is None:
            db.add_all(Series(**series) for series in DEFAULT_SERIES)
            db.commit()
            logger.info("Default series created.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_db()
