from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class ChamadosClientModel(Base):
    """Cliente atendido pelo módulo Deja Chamados."""

    __tablename__ = "chamados_clients"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "document",
            name="uq_chamados_clients_organization_document",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_chamados_clients_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_chamados_clients_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    environment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "environments.id",
            name="fk_chamados_clients_environment_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    fantasy_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    document: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
    )
    contact_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
    )
    whatsapp: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )
    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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
