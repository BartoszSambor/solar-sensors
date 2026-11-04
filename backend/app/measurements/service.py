from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..sensors.models import Sensor
from .models import Measurement
from .schemas import MeasurementCreate


class MeasurementService:
    def get_measurement(self, db: Session, measurement_id: int) -> Measurement | None:
        return db.get(Measurement, measurement_id)

    def list_measurements(
        self,
        db: Session,
        series_ids: list[int] | None,
        from_: datetime | None,
        to: datetime | None,
        descending: bool,
        limit: int,
    ) -> Sequence[Measurement]:
        query = select(Measurement)
        if series_ids:
            query = query.where(Measurement.series_id.in_(series_ids))
        if from_:
            query = query.where(Measurement.timestamp >= from_)
        if to:
            query = query.where(Measurement.timestamp <= to)
        order = Measurement.timestamp.desc() if descending else Measurement.timestamp
        query = query.order_by(order, Measurement.id).limit(limit)
        return db.execute(query).scalars().all()

    def create_measurement(
        self, db: Session, sensor: Sensor, measurement_in: MeasurementCreate
    ) -> Measurement:
        measurement = Measurement(
            series_id=sensor.series_id,
            sensor_id=sensor.id,
            value=measurement_in.value,
            timestamp=measurement_in.timestamp,
        )
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        return measurement


measurement_service = MeasurementService()
