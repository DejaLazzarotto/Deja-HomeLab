from enum import StrEnum


class ChamadosTicketCommentVisibility(StrEnum):
    """Visibilidades permitidas para um comentário de chamado."""

    PUBLIC = "public"
    INTERNAL = "internal"