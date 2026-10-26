"""Modelo da fila persistente de reconhecimento facial do VIVARO."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_platform_api.core.database import Base


class FotosFaceJobModel(Base):
    """Trabalho de reconhecimento facial associado a uma fotografia."""

    __tablename__ = "fotos_face_jobs"

    __table_args__ = (
        UniqueConstraint(
            "media_id",
            name="uq_fotos_face_jobs_media",
        ),
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_fotos_face_jobs_status",
        ),
        CheckConstraint(
            "attempts >= 0 AND max_attempts > 0",
            name="ck_fotos_face_jobs_attempts",
        ),
        Index(
            "ix_fotos_face_jobs_status_schedule",
            "status",
            "next_attempt_at",
            "created_at",
        ),
        Index(
            "ix_fotos_face_jobs_environment_status",
            "environment_id",
            "status",
        ),
        {"mysql_engine": "InnoDB"},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("fotos_media.id", ondelete="CASCADE"),
        nullable=False,
    )

    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    environment_id: Mapped[str] = mapped_column(String(36), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        server_default="3",
    )

    last_error: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    claim_token: Mapped[str | None] = mapped_column(String(36), nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    next_attempt_at: Mapped[datetime | None] = mapped_column(
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
