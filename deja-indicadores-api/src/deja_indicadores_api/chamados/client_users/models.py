from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class ChamadosClientUserModel(Base):
    """Vínculo entre usuário externo e Cliente do Deja Chamados."""

    __tablename__ = "chamados_client_users"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_chamados_client_users_user_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_chamados_client_users_user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    client_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "chamados_clients.id",
            name="fk_chamados_client_users_client_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )