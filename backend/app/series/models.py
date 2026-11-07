from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base


class Series(Base):
    """A measured quantity (e.g. temperature), plotted as a single chart."""

    __tablename__ = "series"
    __table_args__ = (
        CheckConstraint("min_value < max_value", name="ck_series_value_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    min_value: Mapped[float]
    max_value: Mapped[float]
    color: Mapped[str] = mapped_column(String(7))  # "#rrggbb"
    icon: Mapped[str | None] = mapped_column(String(64))
    unit: Mapped[str | None] = mapped_column(String(32))
