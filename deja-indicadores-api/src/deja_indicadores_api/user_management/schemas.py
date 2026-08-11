from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from deja_indicadores_api.user_management.models import (
    UserRole,
    UserStatus,
)


class UserBase(BaseModel):
    """Campos compartilhados de um usuário institucional."""

    organization_id: str = Field(
        min_length=36,
        max_length=36,
    )
    tenant_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )
    environment_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(max_length=255)
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Remove espaços excedentes do nome obrigatório."""

        return value.strip()

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normaliza o e-mail para comparação e persistência."""

        return value.strip().lower()


class UserCreate(UserBase):
    """Dados aceitos no cadastro de um usuário."""


class UserUpdate(UserBase):
    """Dados aceitos na atualização integral de um usuário."""


class UserResponse(UserBase):
    """Representação pública de um usuário."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime