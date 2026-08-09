from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class CompanyStatus(StrEnum):
    """Estados permitidos para uma empresa."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class CompanyModel(Base):
    """Modelo persistente de uma empresa cliente."""

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[str] = mapped_column(String(255), nullable=False)
    document: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
        unique=True,
        index=True,
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[CompanyStatus] = mapped_column(
        Enum(
            CompanyStatus,
            values_callable=lambda statuses: [status.value for status in statuses],
            name="company_status",
        ),
        nullable=False,
        default=CompanyStatus.ACTIVE,
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