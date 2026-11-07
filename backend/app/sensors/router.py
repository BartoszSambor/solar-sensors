from fastapi import APIRouter, HTTPException, Response, status

from ..config import settings
from ..dependencies import DbSession, login_required
from ..errors import problems
from ..series.models import Series
from . import schemas
from .models import Sensor
from .service import sensor_service

# Sensors (and their keys) are admin-only, reads included.
router = APIRouter(dependencies=[login_required], responses=problems(401))


def _get_sensor_or_404(db: DbSession, sensor_id: int) -> Sensor:
    sensor = sensor_service.get_sensor(db, sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found"
        )
    return sensor


@router.get("", response_model=list[schemas.SensorRead])
def list_sensors(db: DbSession) -> list[Sensor]:
    return list(sensor_service.list_sensors(db))


@router.post(
    "",
    response_model=schemas.SensorCreated,
    status_code=status.HTTP_201_CREATED,
    responses=problems(400, 415, 422),
)
def create_sensor(
    sensor_in: schemas.SensorCreate, db: DbSession, response: Response
) -> schemas.SensorCreated:
    if not db.get(Series, sensor_in.series_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Series not found",
        )
    sensor, api_key = sensor_service.create_sensor(db, sensor_in)
    response.headers["Location"] = f"{settings.API_STR}/sensors/{sensor.id}"
    return schemas.SensorCreated(
        **schemas.SensorRead.model_validate(sensor).model_dump(), api_key=api_key
    )


@router.get("/{sensor_id}", response_model=schemas.SensorRead, responses=problems(404))
def get_sensor(sensor_id: int, db: DbSession) -> Sensor:
    return _get_sensor_or_404(db, sensor_id)


@router.delete(
    "/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT, responses=problems(404)
)
def delete_sensor(sensor_id: int, db: DbSession) -> None:
    sensor_service.delete_sensor(db, _get_sensor_or_404(db, sensor_id))
