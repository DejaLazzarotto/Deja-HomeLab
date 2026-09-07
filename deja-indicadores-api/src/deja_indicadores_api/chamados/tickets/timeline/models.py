from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class ChamadosTicketTimelineModel(Base):
    """Evento registrado no histórico de um chamado."""

    __tablename__ = "chamados_ticket_timeline"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    ticket_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "chamados_tickets.id",
            name="fk_chamados_ticket_timeline_ticket_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    previous_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    new_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_chamados_ticket_timeline_created_by_user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True,
    )
