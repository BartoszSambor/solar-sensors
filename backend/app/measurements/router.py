from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, status

from ..dependencies import CurrentSensor, DbSession
from ..series.models import Series
from .models import Measurement
from .schemas import MeasurementCreate, MeasurementRead
from .service import measurement_service

router = APIRouter()


@router.get("", response_model=list[MeasurementRead])
def list_measurements(
    db: DbSession,
    series: Annotated[
        str | None,
        Query(pattern=r"^\d+(,\d+)*$", description="Series ids, e.g. 10,12,23"),
    ] = None,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: datetime | None = None,
    sort: Literal["timestamp", "-timestamp"] = "timestamp",
    limit: Annotated[int, Query(ge=1, le=10000)] = 1000,
) -> list[Measurement]:
    series_ids = [int(i) for i in series.split(",")] if series else None
    return list(
        measurement_service.list_measurements(
            db, series_ids, from_, to, sort == "-timestamp", limit
        )
    )


@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def create_measurement(
    measurement_in: MeasurementCreate, db: DbSession, sensor: CurrentSensor
) -> Measurement:
    """Called by the sensor itself; the X-API-Key header identifies it."""
    series = db.get(Series, sensor.series_id)
    assert series is not None  # guaranteed by the foreign key
    if not series.min_value <= measurement_in.value <= series.max_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Value out of series range "
            f"[{series.min_value}, {series.max_value}]",
        )
    return measurement_service.create_measurement(db, sensor, measurement_in)


@router.get("/{measurement_id}", response_model=MeasurementRead)
def get_measurement(measurement_id: int, db: DbSession) -> Measurement:
    measurement = measurement_service.get_measurement(db, measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found"
        )
    return measurement
