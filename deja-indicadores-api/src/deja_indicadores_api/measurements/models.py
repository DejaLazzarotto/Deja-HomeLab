from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class MeasurementModel(Base):
    """Modelo persistente de uma medição manual de indicador."""

    __tablename__ = "measurements"
    __table_args__ = (
        UniqueConstraint(
            "indicator_id",
            "reference_date",
            name="uq_measurements_indicator_reference_date",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    indicator_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "indicators.id",
            name="fk_measurements_indicator_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    reference_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    actual_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    observation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )