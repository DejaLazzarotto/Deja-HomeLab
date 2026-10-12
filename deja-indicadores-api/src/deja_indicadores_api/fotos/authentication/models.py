"""Modelo de persistencia dos codigos de verificacao do Fotos."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class FotosVerificationPurpose(StrEnum):
    """Finalidades permitidas para um codigo de verificacao."""

    ACTIVATION = "activation"
    PASSWORD_RESET = "password_reset"


class FotosVerificationCodeModel(Base):
    """Codigo temporario de verificacao do Fotos PWA."""

    __tablename__ = "fotos_verification_codes"

    __table_args__ = (
        CheckConstraint(
            "attempts >= 0",
            name="ck_fotos_verification_codes_attempts",
        ),
        CheckConstraint(
            "purpose IN ('activation', 'password_reset')",
            name="ck_fotos_verification_codes_purpose",
        ),
        Index(
            "ix_fotos_verification_codes_user_purpose",
            "user_id",
            "purpose",
        ),
        Index(
            "ix_fotos_verification_codes_expires_at",
            "expires_at",
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
            name="fk_fotos_verification_codes_user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    purpose: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    code_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
    )

    delivery_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    attempts: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
        server_default="0",
    )

    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
    )
