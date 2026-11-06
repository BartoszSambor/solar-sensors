from datetime import datetime

from pydantic import ConfigDict, Field

from ..schemas import CamelModel


class SensorCreate(CamelModel):
    name: str
    series_id: int


class SensorRead(SensorCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    last_measurement_at: datetime | None = Field(
        description="Timestamp of the newest measurement from this sensor; "
        "null until it sends one."
    )


class SensorCreated(SensorRead):
    api_key: str = Field(
        description="Secret for the X-API-Key header. Returned only once."
    )


class SensorsList(CamelModel):
    sensors: list[SensorRead]
