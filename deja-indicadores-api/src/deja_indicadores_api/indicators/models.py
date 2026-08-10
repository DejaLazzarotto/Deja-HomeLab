from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class IndicatorDirection(StrEnum):
    """Direções permitidas para avaliação de um indicador."""

    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"


class IndicatorStatus(StrEnum):
    """Estados permitidos para um indicador."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class IndicatorModel(Base):
    """Modelo persistente de um indicador empresarial."""

    __tablename__ = "indicators"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "name",
            name="uq_indicators_company_name",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "companies.id",
            name="fk_indicators_company_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[IndicatorDirection] = mapped_column(
        Enum(
            IndicatorDirection,
            values_callable=lambda directions: [
                direction.value for direction in directions
            ],
            name="indicator_direction",
        ),
        nullable=False,
    )
    target_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )
    status: Mapped[IndicatorStatus] = mapped_column(
        Enum(
            IndicatorStatus,
            values_callable=lambda statuses: [
                status.value for status in statuses
            ],
            name="indicator_status",
        ),
        nullable=False,
        default=IndicatorStatus.ACTIVE,
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