from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from deja_indicadores_api.module_management.schemas import ModuleKey
from deja_indicadores_api.user_management.models import UserRole


class LoginRequest(BaseModel):
    """Credenciais necessárias para iniciar uma sessão."""

    organization_code: str | None = Field(
        default=None,
        min_length=3,
        max_length=32,
        pattern=r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$",
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("organization_code", mode="before")
    @classmethod
    def normalize_organization_code(
        cls,
        value: object,
    ) -> object:
        """Normaliza o código amigável da organização."""

        if isinstance(value, str):
            normalized_value = value.strip().upper()
            return normalized_value or None

        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        """Normaliza o e-mail antes da validação."""

        if isinstance(value, str):
            return value.strip().lower()

        return value


class AccessTokenResponse(BaseModel):
    """Token JWT emitido após autenticação bem-sucedida."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AccessTokenClaims(BaseModel):
    """Claims obrigatórias aceitas em um token de acesso."""

    sub: str = Field(min_length=36, max_length=36)
    organization_id: str | None = Field(
        min_length=36,
        max_length=36,
    )
    tenant_id: str | None = Field(min_length=36, max_length=36)
    environment_id: str | None = Field(min_length=36, max_length=36)
    role: UserRole
    type: Literal["access"]
    iat: int
    exp: int
    jti: UUID


class AuthenticatedUser(BaseModel):
    """Identidade, escopo e módulos do usuário autenticado."""

    id: str
    organization_id: str | None
    tenant_id: str | None
    environment_id: str | None
    name: str
    email: EmailStr
    role: UserRole
    enabled_modules: list[ModuleKey] = Field(default_factory=list)
