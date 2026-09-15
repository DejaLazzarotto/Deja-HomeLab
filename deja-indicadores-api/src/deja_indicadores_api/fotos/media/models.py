from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class FotosMediaModel(Base):
    """Mídia original armazenada pelo módulo Deja Fotos."""

    __tablename__ = "fotos_media"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_fotos_media_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_fotos_media_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    environment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "environments.id",
            name="fk_fotos_media_environment_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    album_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "fotos_albums.id",
            name="fk_fotos_media_album_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    original_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    media_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
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

    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    original_storage_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        unique=True,
    )

    processing_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="received",
        index=True,
    )

    processing_error: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    original_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    view_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    created_by_user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_fotos_media_created_by_user_id",
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )