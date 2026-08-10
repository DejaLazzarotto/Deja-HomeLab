from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deja_indicadores_api.tenant_management.models import (
    TenantManagementStatus,
)


class NamedResourceBase(BaseModel):
    """Campos compartilhados pelos recursos do Tenant Management."""

    name: str = Field(min_length=1, max_length=255)
    status: TenantManagementStatus = TenantManagementStatus.PROVISIONING

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Remove espaços excedentes do nome obrigatório."""

        return value.strip()


class OrganizationBase(NamedResourceBase):
    """Campos compartilhados de uma organização."""


class OrganizationCreate(OrganizationBase):
    """Dados aceitos no cadastro de uma organização."""


class OrganizationUpdate(OrganizationBase):
    """Dados aceitos na atualização integral de uma organização."""


class OrganizationResponse(OrganizationBase):
    """Representação pública de uma organização."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class TenantBase(NamedResourceBase):
    """Campos compartilhados de um tenant."""

    organization_id: str = Field(
        min_length=36,
        max_length=36,
    )


class TenantCreate(TenantBase):
    """Dados aceitos no cadastro de um tenant."""


class TenantUpdate(TenantBase):
    """Dados aceitos na atualização integral de um tenant."""


class TenantResponse(TenantBase):
    """Representação pública de um tenant."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class EnvironmentBase(NamedResourceBase):
    """Campos compartilhados de um ambiente."""

    tenant_id: str = Field(
        min_length=36,
        max_length=36,
    )


class EnvironmentCreate(EnvironmentBase):
    """Dados aceitos no cadastro de um ambiente."""


class EnvironmentUpdate(EnvironmentBase):
    """Dados aceitos na atualização integral de um ambiente."""


class EnvironmentResponse(EnvironmentBase):
    """Representação pública de um ambiente."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime