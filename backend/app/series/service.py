from collections.abc import Sequence

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from ..measurements.models import Measurement
from .models import Series
from .schemas import SeriesCreate


class SeriesService:
    def get_series(self, db: Session, series_id: int) -> Series | None:
        return db.get(Series, series_id)

    def get_series_by_name(self, db: Session, name: str) -> Series | None:
        return db.execute(select(Series).where(Series.name == name)).scalar()

    def has_measurements_outside(
        self, db: Session, series_id: int, min_value: float, max_value: float
    ) -> bool:
        """True if any stored measurement of the series falls outside [min, max]."""
        return bool(
            db.scalar(
                select(
                    exists().where(
                        Measurement.series_id == series_id,
                        or_(
                            Measurement.value < min_value,
                            Measurement.value > max_value,
                        ),
                    )
                )
            )
        )

    def list_series(self, db: Session) -> Sequence[Series]:
        return db.execute(select(Series).order_by(Series.id)).scalars().all()

    def create_series(self, db: Session, series_in: SeriesCreate) -> Series:
        series = Series(**series_in.model_dump())
        db.add(series)
        db.commit()
        db.refresh(series)
        return series

    def update_series(
        self, db: Session, series: Series, series_in: SeriesCreate
    ) -> Series:
        for field, value in series_in.model_dump().items():
            setattr(series, field, value)
        db.commit()
        db.refresh(series)
        return series

    def delete_series(self, db: Session, series: Series) -> None:
        # The database cascades the delete to the series' sensors and measurements.
        db.delete(series)
        db.commit()


series_service = SeriesService()
