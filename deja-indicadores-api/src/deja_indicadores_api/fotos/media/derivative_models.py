from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class FotosMediaDerivativeModel(Base):
    """Arquivo derivado gerado a partir de uma mídia original."""

    __tablename__ = "fotos_media_derivatives"
    __table_args__ = (
        UniqueConstraint(
            "media_id",
            "derivative_type",
            name="uq_fotos_media_derivatives_media_type",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "fotos_media.id",
            name="fk_fotos_media_derivatives_media_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    derivative_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    storage_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        unique=True,
    )

    content_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_extension: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True,
    )