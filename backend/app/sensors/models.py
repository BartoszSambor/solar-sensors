from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base, TimeStampMixin


class Sensor(Base, TimeStampMixin):
    __tablename__ = "sensor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    # Deleting a series deletes its sensors.
    series_id: Mapped[int] = mapped_column(
        ForeignKey("series.id", ondelete="CASCADE"), index=True
    )
    # The API key is shown once on creation; only its hash is stored.
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True)
    # Timestamp of the newest measurement this sensor sent (None: none yet).
    # Kept up to date by measurement_service.create_measurement.
    last_measurement_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
