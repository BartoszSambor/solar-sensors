from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base, TimeStampMixin


class Sensor(Base, TimeStampMixin):
    __tablename__ = "sensor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    series: Mapped[str] = mapped_column(String(255))
