from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deja_indicadores_api.indicators.models import (
    IndicatorDirection,
    IndicatorStatus,
)


class IndicatorBase(BaseModel):
    """Campos compartilhados para criação e atualização de indicadores."""

    company_id: str = Field(
        min_length=36,
        max_length=36,
    )
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    unit: str = Field(min_length=1, max_length=50)
    direction: IndicatorDirection
    target_value: Decimal = Field(
        max_digits=18,
        decimal_places=4,
    )
    status: IndicatorStatus = IndicatorStatus.ACTIVE

    @field_validator("name", "unit", mode="before")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        """Remove espaços excedentes dos campos obrigatórios."""

        return value.strip()

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        """Normaliza a descrição quando informada."""

        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class IndicatorCreate(IndicatorBase):
    """Dados aceitos no cadastro de um indicador."""


class IndicatorUpdate(IndicatorBase):
    """Dados aceitos na atualização integral de um indicador."""


class IndicatorResponse(IndicatorBase):
    """Representação pública de um indicador retornado pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime