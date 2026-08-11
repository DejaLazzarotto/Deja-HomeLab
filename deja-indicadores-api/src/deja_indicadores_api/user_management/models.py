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


class UserRole(StrEnum):
    """Papéis institucionais permitidos para usuários."""

    ORGANIZATION_ADMIN = "organization_admin"
    TENANT_ADMIN = "tenant_admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserStatus(StrEnum):
    """Estados permitidos para usuários."""

    ACTIVE = "active"
    INACTIVE = "inactive"


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
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_users_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
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
            values_callable=lambda roles: [role.value for role in roles],
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