from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
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