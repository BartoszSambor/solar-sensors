from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .models import Sensor
from .schemas import SensorCreate, SensorRead, SensorsList


class SensorService:
    def get_sensor(self, db: Session, sensor_id: int) -> Sensor | None:
        query = select(Sensor).where(Sensor.id == sensor_id)
        return db.execute(query).scalar_one_or_none()

    def list_sensors(self, db: Session) -> SensorsList:
        query = select(Sensor).order_by(desc(Sensor.created_at))
        sensors = db.execute(query).scalars().all()
        return SensorsList(
            sensors=[SensorRead.model_validate(sensor) for sensor in sensors],
        )

    def create_sensor(self, db: Session, sensor_in: SensorCreate) -> Sensor:
        sensor = Sensor(name=sensor_in.name, series=sensor_in.seriesId)
        db.add(sensor)
        db.commit()
        db.refresh(sensor)
        return sensor

    def delete_sensor(self, db: Session, sensor: Sensor) -> None:
        db.delete(sensor)
        db.commit()


sensor_service = SensorService()
