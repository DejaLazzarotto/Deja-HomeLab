from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from deja_indicadores_api.core.database import Base
from deja_indicadores_api.module_management.models import MODULE_KEY_LENGTH


class UserRole(StrEnum):
    """Papéis institucionais permitidos para usuários."""

    PLATFORM_ADMIN = "platform_admin"
    ORGANIZATION_ADMIN = "organization_admin"
    TENANT_ADMIN = "tenant_admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    CLIENT = "client"


class UserStatus(StrEnum):
    """Estados permitidos para usuários."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class UserModuleRole(StrEnum):
    """Papéis funcionais permitidos dentro de um módulo."""

    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserModel(Base):
    """Modelo persistente de um usuário institucional."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "email",
            name="uq_users_organization_email",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    organization_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_users_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )
    tenant_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_users_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )
    environment_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "environments.id",
            name="fk_users_environment_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            values_callable=lambda roles: [
                role.value for role in roles
            ],
            name="user_role",
        ),
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(
            UserStatus,
            values_callable=lambda statuses: [
                status.value for status in statuses
            ],
            name="user_status",
        ),
        nullable=False,
        default=UserStatus.ACTIVE,
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


class UserModuleAccessModel(Base):
    """Acesso funcional de um usuário a um módulo da plataforma."""

    __tablename__ = "user_module_access"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "users.id",
            name="fk_user_module_access_user_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    module_key: Mapped[str] = mapped_column(
        String(MODULE_KEY_LENGTH),
        ForeignKey(
            "modules.key",
            name="fk_user_module_access_module_key",
            ondelete="RESTRICT",
        ),
        primary_key=True,
        index=True,
    )
    role: Mapped[UserModuleRole] = mapped_column(
        Enum(
            UserModuleRole,
            values_callable=lambda roles: [
                role.value for role in roles
            ],
            name="user_module_role",
        ),
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