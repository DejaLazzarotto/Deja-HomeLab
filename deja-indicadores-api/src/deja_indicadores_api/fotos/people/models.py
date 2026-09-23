"""Modelos de pessoas e vínculos com mídias do Deja Fotos."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base


class FotosPersonModel(Base):
    """Pessoa cadastrada em um ambiente do Deja Fotos."""

    __tablename__ = "fotos_people"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "tenant_id",
            "environment_id",
            "name",
            name="uq_fotos_people_scope_name",
        ),
        UniqueConstraint(
            "avatar_storage_key",
            name="uq_fotos_people_avatar_storage_key",
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
            name="fk_fotos_people_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_fotos_people_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    environment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "environments.id",
            name="fk_fotos_people_environment_id",
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
        server_default=true(),
    )

    avatar_storage_key: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    avatar_content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    avatar_file_size: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    avatar_checksum_sha256: Mapped[str | None] = mapped_column(
        String(64),
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


class FotosPersonMediaModel(Base):
    """Vínculo confirmado entre uma pessoa e uma mídia."""

    __tablename__ = "fotos_person_media"

    person_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "fotos_people.id",
            name="fk_fotos_person_media_person_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "fotos_media.id",
            name="fk_fotos_person_media_media_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        index=True,
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_fotos_person_media_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_fotos_person_media_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    environment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "environments.id",
            name="fk_fotos_person_media_environment_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )