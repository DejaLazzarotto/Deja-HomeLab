from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from deja_indicadores_api.module_management.schemas import ModuleKey
from deja_indicadores_api.user_management.models import (
    UserModuleRole,
    UserRole,
    UserStatus,
)


class UserBase(BaseModel):
    """Campos compartilhados de um usuário institucional."""

    organization_id: str | None = Field(
        default=None,
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
    name: str = Field(
        min_length=1,
        max_length=255,
    )
    email: EmailStr = Field(
        max_length=255,
    )
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(
        cls,
        value: str,
    ) -> str:
        """Remove espaços excedentes do nome obrigatório."""

        return value.strip()

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(
        cls,
        value: str,
    ) -> str:
        """Normaliza o e-mail para comparação e persistência."""

        return value.strip().lower()


class UserCreate(UserBase):
    """Dados aceitos no cadastro de um usuário."""


class UserUpdate(UserBase):
    """Dados aceitos na atualização integral de um usuário."""


class UserPasswordSet(BaseModel):
    """Dados aceitos na definição ou alteração da senha."""

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(UserBase):
    """Representação pública de um usuário."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    created_at: datetime
    updated_at: datetime


class UserModuleAccessInput(BaseModel):
    """Acesso funcional solicitado para um módulo."""

    module_key: ModuleKey
    role: UserModuleRole

    @field_validator("module_key", mode="before")
    @classmethod
    def normalize_module_key(
        cls,
        value: object,
    ) -> object:
        """Remove espaços excedentes da chave do módulo."""

        if isinstance(value, str):
            return value.strip()

        return value


class UserModuleAccessUpdate(BaseModel):
    """Seleção integral de acessos funcionais do usuário."""

    modules: list[UserModuleAccessInput] = Field(
        default_factory=list,
    )

    @field_validator("modules")
    @classmethod
    def reject_duplicate_module_keys(
        cls,
        value: list[UserModuleAccessInput],
    ) -> list[UserModuleAccessInput]:
        """Rejeita módulos repetidos na mesma seleção."""

        module_keys = [
            module.module_key
            for module in value
        ]

        if len(module_keys) != len(set(module_keys)):
            raise ValueError(
                "A seleção de módulos contém chaves duplicadas."
            )

        return value


class UserModuleAccessResponse(BaseModel):
    """Estado de acesso de um módulo para um usuário."""

    key: ModuleKey
    name: str
    description: str | None
    display_order: int
    organization_enabled: bool
    has_access: bool
    role: UserModuleRole | None


class UserModuleAccessesResponse(BaseModel):
    """Catálogo de módulos aplicado a um usuário."""

    user_id: str
    modules: list[UserModuleAccessResponse]