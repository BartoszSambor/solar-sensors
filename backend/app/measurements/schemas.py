from datetime import datetime

from pydantic import AwareDatetime, ConfigDict, Field

from ..schemas import CamelModel


class MeasurementCreate(CamelModel):
    value: float
    timestamp: AwareDatetime | None = Field(
        default=None, description="Defaults to the server's current time."
    )


class MeasurementRead(CamelModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    series_id: int
    # Omitted from responses once the sensor is deleted.
    sensor_id: int | None = None
    value: float
    timestamp: datetime
