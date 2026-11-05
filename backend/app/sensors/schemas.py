from pydantic import ConfigDict, Field

from ..schemas import CamelModel


class SensorCreate(CamelModel):
    name: str
    series_id: int


class SensorRead(SensorCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SensorCreated(SensorRead):
    api_key: str = Field(
        description="Secret for the X-API-Key header. Returned only once."
    )


class SensorsList(CamelModel):
    sensors: list[SensorRead]
