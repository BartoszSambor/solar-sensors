from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..auth.security import generate_token, hash_token
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

    def get_sensor_by_api_key(self, db: Session, api_key: str) -> Sensor | None:
        query = select(Sensor).where(Sensor.api_key_hash == hash_token(api_key))
        return db.execute(query).scalar_one_or_none()

    def create_sensor(self, db: Session, sensor_in: SensorCreate) -> tuple[Sensor, str]:
        """Returns the sensor and its API key (the only time it's available)."""
        api_key = generate_token()
        sensor = Sensor(
            name=sensor_in.name,
            series_id=sensor_in.series_id,
            api_key_hash=hash_token(api_key),
        )
        db.add(sensor)
        db.commit()
        db.refresh(sensor)
        return sensor, api_key

    def delete_sensor(self, db: Session, sensor: Sensor) -> None:
        db.delete(sensor)
        db.commit()


sensor_service = SensorService()
