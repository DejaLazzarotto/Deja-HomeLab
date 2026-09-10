from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deja_indicadores_api.chamados.tickets.comments.enums import (
    ChamadosTicketCommentVisibility,
)


class ChamadosTicketCommentCreate(BaseModel):
    """Dados para criação de um comentário em chamado."""

    content: str = Field(
        min_length=1,
        max_length=5000,
    )
    visibility: ChamadosTicketCommentVisibility = (
        ChamadosTicketCommentVisibility.PUBLIC
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        """Remove espaços externos e rejeita conteúdo vazio."""

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("O comentário não pode ser vazio.")

        return normalized_value


class ChamadosTicketCommentResponse(BaseModel):
    """Representação de um comentário de chamado."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    content: str
    visibility: ChamadosTicketCommentVisibility
    created_by_user_id: str | None
    created_at: datetime