"""Contratos da API de Pessoas do Deja Fotos."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deja_indicadores_api.fotos.media.schemas import (
    FotosMediaResponse,
)


class FotosPersonBase(BaseModel):
    """Campos editáveis de uma pessoa."""

    environment_id: str = Field(
        min_length=36,
        max_length=36,
    )

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    active: bool = True

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Remove espaços excedentes do nome."""

        return value.strip()

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        """Normaliza as observações opcionais."""

        if value is None:
            return None

        return value.strip() or None


class FotosPersonCreate(FotosPersonBase):
    """Dados aceitos para cadastrar uma pessoa."""


class FotosPersonUpdate(FotosPersonBase):
    """Dados aceitos para atualizar uma pessoa."""


class FotosPersonResponse(FotosPersonBase):
    """Representação pública de uma pessoa."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    tenant_id: str
    avatar_content_type: str | None
    created_at: datetime
    updated_at: datetime


class FotosPersonListResponse(BaseModel):
    """Página de pessoas dentro do escopo autorizado."""

    items: list[FotosPersonResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class FotosPersonMediaLink(BaseModel):
    """Mídia a vincular manualmente à pessoa."""

    media_id: str = Field(
        min_length=36,
        max_length=36,
    )


class FotosPersonMediaListResponse(BaseModel):
    """Página das mídias vinculadas a uma pessoa."""

    items: list[FotosMediaResponse]
    page: int
    page_size: int
    total: int
    total_pages: int