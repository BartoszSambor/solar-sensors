from pydantic import ConfigDict

from ..schemas import CamelModel


class SensorCreate(CamelModel):
    name: str
    series_id: int


class SensorRead(SensorCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SensorsList(CamelModel):
    sensors: list[SensorRead]
