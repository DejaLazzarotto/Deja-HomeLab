from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base

MODULE_KEY_LENGTH = 64


class ModuleModel(Base):
    """Módulo comercial instalado na plataforma."""

    __tablename__ = "modules"

    key: Mapped[str] = mapped_column(
        String(MODULE_KEY_LENGTH),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
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


class OrganizationModuleModel(Base):
    """Liberação de um módulo comercial para uma organização."""

    __tablename__ = "organization_modules"

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_organization_modules_organization_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        index=True,
    )
    module_key: Mapped[str] = mapped_column(
        String(MODULE_KEY_LENGTH),
        ForeignKey(
            "modules.key",
            name="fk_organization_modules_module_key",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
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