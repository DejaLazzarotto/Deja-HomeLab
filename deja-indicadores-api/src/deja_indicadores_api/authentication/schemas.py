from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from deja_indicadores_api.user_management.models import UserRole


class LoginRequest(BaseModel):
    """Credenciais necessárias para iniciar uma sessão."""

    organization_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )

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
    """Identidade e escopo institucional do usuário autenticado."""

    id: str
    organization_id: str | None
    tenant_id: str | None
    environment_id: str | None
    name: str
    email: EmailStr
    role: UserRole