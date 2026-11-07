from typing import Self

from pydantic import ConfigDict, Field, model_validator

from ..schemas import CamelModel


class SeriesCreate(CamelModel):
    name: str = Field(min_length=1, max_length=100)
    min_value: float
    max_value: float
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$", examples=["#1f77b4"])
    icon: str | None = Field(
        default=None,
        max_length=64,
        description="Optional icon or chart marker name",
    )
    unit: str | None = Field(default=None, max_length=20, examples=["°C"])

    @model_validator(mode="after")
    def check_range(self) -> Self:
        if self.min_value >= self.max_value:
            raise ValueError("minValue must be less than maxValue")
        return self


class SeriesRead(SeriesCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
