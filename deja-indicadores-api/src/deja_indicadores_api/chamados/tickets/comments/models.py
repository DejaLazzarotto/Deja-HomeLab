from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.chamados.tickets.comments.enums import (
    ChamadosTicketCommentVisibility,
)
from deja_indicadores_api.core.database import Base


class ChamadosTicketCommentModel(Base):
    """Comentário registrado em um chamado."""

    __tablename__ = "chamados_ticket_comments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    ticket_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "chamados_tickets.id",
            name="fk_chamados_ticket_comments_ticket_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    visibility: Mapped[ChamadosTicketCommentVisibility] = mapped_column(
        Enum(
            ChamadosTicketCommentVisibility,
            values_callable=lambda visibilities: [
                visibility.value for visibility in visibilities
            ],
            name="chamados_ticket_comment_visibility",
        ),
        nullable=False,
        default=ChamadosTicketCommentVisibility.PUBLIC,
        index=True,
    )
    created_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_chamados_ticket_comments_created_by_user_id",
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