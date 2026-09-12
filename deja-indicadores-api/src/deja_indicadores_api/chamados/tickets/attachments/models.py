from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class ChamadosTicketAttachmentModel(Base):
    """Anexo vinculado a um chamado."""

    __tablename__ = "chamados_ticket_attachments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    ticket_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "chamados_tickets.id",
            name="fk_chamados_ticket_attachments_ticket_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    original_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    created_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_chamados_ticket_attachments_created_by_user_id",
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