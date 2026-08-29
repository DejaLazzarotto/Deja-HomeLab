from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deja_indicadores_api.chamados.tickets.enums import (
    ChamadosTicketPriority,
    ChamadosTicketStatus,
)


class ChamadosTicketCreate(BaseModel):
    """Dados aceitos na abertura de um chamado."""

    model_config = ConfigDict(extra="forbid")

    environment_id: str = Field(
        min_length=36,
        max_length=36,
    )
    client_id: str = Field(
        min_length=36,
        max_length=36,
    )
    title: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str = Field(
        min_length=1,
        max_length=5000,
    )
    priority: ChamadosTicketPriority = ChamadosTicketPriority.MEDIUM
    assigned_to_user_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        """Remove espaços excedentes dos textos obrigatórios."""

        return value.strip()


class ChamadosTicketUpdate(BaseModel):
    """Dados aceitos na atualização operacional de um chamado."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str = Field(
        min_length=1,
        max_length=5000,
    )
    priority: ChamadosTicketPriority
    assigned_to_user_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        """Remove espaços excedentes dos textos obrigatórios."""

        return value.strip()


class ChamadosTicketStatusUpdate(BaseModel):
    """Novo estado solicitado para um chamado."""

    model_config = ConfigDict(extra="forbid")

    status: ChamadosTicketStatus


class ChamadosTicketResponse(BaseModel):
    """Representação pública de um chamado."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    tenant_id: str
    environment_id: str
    client_id: str

    title: str
    description: str
    status: ChamadosTicketStatus
    priority: ChamadosTicketPriority

    opened_by_user_id: str
    assigned_to_user_id: str | None
    assigned_to_user_name: str | None
    closed_by_user_id: str | None
    closed_at: datetime | None

    created_at: datetime
    updated_at: datetime