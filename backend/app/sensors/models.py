from sqlalchemy import ForeignKey, String
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
