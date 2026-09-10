from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deja_indicadores_api.chamados.tickets.enums import (
    ChamadosTicketPriority,
    ChamadosTicketStatus,
)


class ChamadosPortalTicketCreate(BaseModel):
    """Dados aceitos para abertura de chamado pelo Portal."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        min_length=1,
        max_length=150,
    )
    description: str = Field(
        min_length=1,
        max_length=5000,
    )

    @field_validator(
        "title",
        "description",
        mode="before",
    )
    @classmethod
    def normalize_required_text(
        cls,
        value: str,
    ) -> str:
        """Remove espaços excedentes dos textos obrigatórios."""

        return value.strip()


class ChamadosPortalTicketResponse(BaseModel):
    """Representação segura de um chamado no Portal externo."""

    model_config = ConfigDict(from_attributes=True)

    id: str

    title: str
    description: str
    status: ChamadosTicketStatus
    priority: ChamadosTicketPriority

    assigned_to_user_name: str | None
    closed_at: datetime | None

    created_at: datetime
    updated_at: datetime


class ChamadosPortalTimelineResponse(BaseModel):
    """Representação segura de um evento do histórico no Portal."""

    id: str
    event_type: str
    description: str

    previous_value: str | None
    new_value: str | None

    created_at: datetime


class ChamadosPortalCommentCreate(BaseModel):
    """Dados aceitos para comentário público criado pelo Portal."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(
        min_length=1,
        max_length=5000,
    )

    @field_validator(
        "content",
        mode="before",
    )
    @classmethod
    def normalize_content(
        cls,
        value: str,
    ) -> str:
        """Remove espaços excedentes do comentário."""

        return value.strip()


class ChamadosPortalCommentResponse(BaseModel):
    """Representação segura de comentário público no Portal."""

    id: str
    content: str
    created_by: str | None
    created_at: datetime