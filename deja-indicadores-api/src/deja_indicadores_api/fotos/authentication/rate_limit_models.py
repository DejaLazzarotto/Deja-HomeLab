"""Persistencia dos limites de requisicoes da autenticacao Fotos."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class FotosAuthRateLimitModel(Base):
    """Contador compartilhado de requisicoes por janela de tempo."""

    __tablename__ = "fotos_auth_rate_limits"

    __table_args__ = (
        UniqueConstraint(
            "scope",
            "subject_hash",
            "window_start",
            name="uq_fotos_auth_rate_limits_window",
        ),
        CheckConstraint(
            "scope IN ('ip', 'account', 'confirm_ip', 'confirm_account')",
            name="ck_fotos_auth_rate_limits_scope",
        ),
        CheckConstraint(
            "request_count >= 0",
            name="ck_fotos_auth_rate_limits_count",
        ),
        Index(
            "ix_fotos_auth_rate_limits_window_start",
            "window_start",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    scope: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    subject_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    window_start: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
    )

    request_count: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
        server_default="0",
    )
