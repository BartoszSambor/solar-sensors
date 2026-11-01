from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base


class Measurement(Base):
    __tablename__ = "measurement"
    # Charts read one series over a time range.
    __table_args__ = (
        Index("ix_measurement_series_id_timestamp", "series_id", "timestamp"),
    )

    # SQLite only autoincrements INTEGER primary keys (unit tests).
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    # Deleting a series deletes its measurements...
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id", ondelete="CASCADE"))
    # ...while deleting a sensor keeps them, just unlinked.
    sensor_id: Mapped[int | None] = mapped_column(
        ForeignKey("sensor.id", ondelete="SET NULL"), index=True
    )
    value: Mapped[float]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
