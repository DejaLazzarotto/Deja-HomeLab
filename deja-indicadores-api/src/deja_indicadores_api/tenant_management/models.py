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


class TenantManagementStatus(StrEnum):
    """Estados permitidos para recursos do Tenant Management."""

    PROVISIONING = "provisioning"
    ACTIVE = "active"
    INACTIVE = "inactive"


class OrganizationModel(Base):
    """Modelo persistente de uma organização."""

    __tablename__ = "organizations"
    __table_args__ = (
        UniqueConstraint(
            "name",
            name="uq_organizations_name",
        ),
        UniqueConstraint(
            "code",
            name="uq_organizations_code",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    status: Mapped[TenantManagementStatus] = mapped_column(
        Enum(
            TenantManagementStatus,
            values_callable=lambda statuses: [status.value for status in statuses],
            name="organization_status",
        ),
        nullable=False,
        default=TenantManagementStatus.PROVISIONING,
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


class TenantModel(Base):
    """Modelo persistente de um tenant organizacional."""

    __tablename__ = "tenants"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_tenants_organization_name",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "organizations.id",
            name="fk_tenants_organization_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TenantManagementStatus] = mapped_column(
        Enum(
            TenantManagementStatus,
            values_callable=lambda statuses: [status.value for status in statuses],
            name="tenant_status",
        ),
        nullable=False,
        default=TenantManagementStatus.PROVISIONING,
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


class EnvironmentModel(Base):
    """Modelo persistente de um ambiente pertencente a um tenant."""

    __tablename__ = "environments"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "name",
            name="uq_environments_tenant_name",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "tenants.id",
            name="fk_environments_tenant_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TenantManagementStatus] = mapped_column(
        Enum(
            TenantManagementStatus,
            values_callable=lambda statuses: [status.value for status in statuses],
            name="environment_status",
        ),
        nullable=False,
        default=TenantManagementStatus.PROVISIONING,
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
