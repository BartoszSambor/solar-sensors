from pydantic import BaseModel, ConfigDict, Field


class SensorCreate(BaseModel):
    name: str
    seriesId: str


class SensorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    seriesId: str = Field(validation_alias="series")


class SensorsList(BaseModel):
    sensors: list[SensorRead]
