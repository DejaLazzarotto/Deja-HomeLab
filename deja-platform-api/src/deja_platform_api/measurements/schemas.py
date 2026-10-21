from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MeasurementBase(BaseModel):
    """Campos compartilhados para criação e atualização de medições."""

    indicator_id: str = Field(
        min_length=36,
        max_length=36,
    )
    reference_date: date
    actual_value: Decimal = Field(
        max_digits=18,
        decimal_places=4,
    )
    observation: str | None = None

    @field_validator("observation", mode="before")
    @classmethod
    def normalize_observation(cls, value: str | None) -> str | None:
        """Normaliza a observação quando informada."""

        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class MeasurementCreate(MeasurementBase):
    """Dados aceitos no cadastro de uma medição manual."""


class MeasurementUpdate(MeasurementBase):
    """Dados aceitos na atualização integral de uma medição manual."""


class MeasurementResponse(MeasurementBase):
    """Representação pública de uma medição retornada pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_by: str | None
    created_at: datetime
    updated_at: datetime