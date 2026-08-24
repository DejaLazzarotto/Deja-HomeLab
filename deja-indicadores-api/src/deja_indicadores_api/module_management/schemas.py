from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from deja_indicadores_api.module_management.models import (
    MODULE_KEY_LENGTH,
)

ModuleKey = Annotated[
    str,
    Field(
        min_length=1,
        max_length=MODULE_KEY_LENGTH,
        pattern=r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$",
    ),
]


class ModuleResponse(BaseModel):
    """Representação pública de um módulo instalado."""

    model_config = ConfigDict(from_attributes=True)

    key: ModuleKey
    name: str
    description: str | None
    display_order: int
    created_at: datetime
    updated_at: datetime


class OrganizationModuleResponse(BaseModel):
    """Módulo do catálogo com o estado de uma organização."""

    key: ModuleKey
    name: str
    description: str | None
    display_order: int
    enabled: bool


class OrganizationModulesResponse(BaseModel):
    """Catálogo completo aplicado a uma organização."""

    organization_id: str
    modules: list[OrganizationModuleResponse]


class OrganizationModulesUpdate(BaseModel):
    """Seleção integral de módulos habilitados para uma organização."""

    enabled_modules: list[ModuleKey] = Field(default_factory=list)

    @field_validator("enabled_modules", mode="before")
    @classmethod
    def normalize_module_keys(cls, value: object) -> object:
        """Remove espaços excedentes das chaves recebidas."""

        if not isinstance(value, list):
            return value

        return [
            item.strip()
            if isinstance(item, str)
            else item
            for item in value
        ]

    @field_validator("enabled_modules")
    @classmethod
    def reject_duplicate_module_keys(
        cls,
        value: list[str],
    ) -> list[str]:
        """Rejeita a repetição de uma chave na seleção."""

        if len(value) != len(set(value)):
            raise ValueError(
                "A seleção de módulos contém chaves duplicadas."
            )

        return value