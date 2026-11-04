from datetime import datetime

from pydantic import AwareDatetime, ConfigDict

from ..schemas import CamelModel


class MeasurementCreate(CamelModel):
    value: float
    timestamp: AwareDatetime


class MeasurementRead(CamelModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    series_id: int
    sensor_id: int | None
    value: float
    timestamp: datetime
