from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.chamados.tickets.enums import (
    ChamadosTicketPriority,
    ChamadosTicketStatus,
)
from deja_indicadores_api.core.database import Base


class ChamadosTicketModel(Base):
    """Chamado operacional do módulo Deja Chamados."""

    __tablename__ = "chamados_tickets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_chamados_tickets_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_chamados_tickets_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    environment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "environments.id",
            name="fk_chamados_tickets_environment_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    client_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "chamados_clients.id",
            name="fk_chamados_tickets_client_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[ChamadosTicketStatus] = mapped_column(
        Enum(
            ChamadosTicketStatus,
            values_callable=lambda statuses: [
                status.value for status in statuses
            ],
            name="chamados_ticket_status",
        ),
        nullable=False,
        default=ChamadosTicketStatus.OPEN,
        index=True,
    )
    priority: Mapped[ChamadosTicketPriority] = mapped_column(
        Enum(
            ChamadosTicketPriority,
            values_callable=lambda priorities: [
                priority.value for priority in priorities
            ],
            name="chamados_ticket_priority",
        ),
        nullable=False,
        default=ChamadosTicketPriority.MEDIUM,
        index=True,
    )

    opened_by_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_chamados_tickets_opened_by_user_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    assigned_to_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_chamados_tickets_assigned_to_user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    closed_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_chamados_tickets_closed_by_user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
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