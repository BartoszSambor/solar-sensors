from fastapi import APIRouter, HTTPException, status

from ..dependencies import DbSession, login_required
from ..series.models import Series
from . import schemas
from .models import Sensor
from .service import sensor_service

router = APIRouter()


def _get_sensor_or_404(db: DbSession, sensor_id: int) -> Sensor:
    sensor = sensor_service.get_sensor(db, sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found"
        )
    return sensor


@router.get("/", response_model=schemas.SensorsList)
def list_sensors(db: DbSession) -> schemas.SensorsList:
    return sensor_service.list_sensors(db)


@router.post(
    "/",
    response_model=schemas.SensorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[login_required],
)
def create_sensor(sensor_in: schemas.SensorCreate, db: DbSession) -> Sensor:
    if not db.get(Series, sensor_in.series_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Series not found",
        )
    return sensor_service.create_sensor(db, sensor_in)


@router.get("/{sensor_id}", response_model=schemas.SensorRead)
def get_sensor(sensor_id: int, db: DbSession) -> Sensor:
    return _get_sensor_or_404(db, sensor_id)


@router.delete(
    "/{sensor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[login_required],
)
def delete_sensor(sensor_id: int, db: DbSession) -> None:
    sensor_service.delete_sensor(db, _get_sensor_or_404(db, sensor_id))
