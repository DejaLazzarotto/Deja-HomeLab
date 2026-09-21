from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class FotosAlbumModel(Base):
    """Álbum de mídias do módulo Deja Fotos."""

    __tablename__ = "fotos_albums"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "tenant_id",
            "environment_id",
            "name",
            name="uq_fotos_albums_scope_name",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_fotos_albums_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_fotos_albums_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    environment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "environments.id",
            name="fk_fotos_albums_environment_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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


class FotosAlbumPeriodDescriptionModel(Base):
    """Descrição persistida de um mês específico de um álbum."""

    __tablename__ = "fotos_album_period_descriptions"
    __table_args__ = (
        UniqueConstraint(
            "album_id",
            "original_year",
            "original_month",
            name="uq_fotos_album_period_descriptions_period",
        ),
        CheckConstraint(
            "original_year >= 1 AND original_year <= 9999",
            name="ck_fotos_album_period_descriptions_year",
        ),
        CheckConstraint(
            "original_month >= 1 AND original_month <= 12",
            name="ck_fotos_album_period_descriptions_month",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name=(
                "fk_fotos_album_period_descriptions_"
                "organization_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_fotos_album_period_descriptions_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    environment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "environments.id",
            name=(
                "fk_fotos_album_period_descriptions_"
                "environment_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    album_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "fotos_albums.id",
            name="fk_fotos_album_period_descriptions_album_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    original_year: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    original_month: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
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