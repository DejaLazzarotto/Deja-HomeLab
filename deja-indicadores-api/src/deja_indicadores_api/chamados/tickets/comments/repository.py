from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.chamados.tickets.comments.enums import (
    ChamadosTicketCommentVisibility,
)
from deja_indicadores_api.chamados.tickets.comments.models import (
    ChamadosTicketCommentModel,
)


class ChamadosTicketCommentRepository:
    """Persistência dos comentários de chamados."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_ticket_id(
        self,
        ticket_id: str,
        *,
        visibility: ChamadosTicketCommentVisibility | None = None,
    ) -> list[ChamadosTicketCommentModel]:
        """Lista comentários de um chamado em ordem cronológica."""

        statement = select(ChamadosTicketCommentModel).where(
            ChamadosTicketCommentModel.ticket_id == ticket_id
        )

        if visibility is not None:
            statement = statement.where(
                ChamadosTicketCommentModel.visibility == visibility
            )

        statement = statement.order_by(
            ChamadosTicketCommentModel.created_at.asc()
        )

        return list(
            self._session.scalars(statement).all()
        )

    def add(
        self,
        comment: ChamadosTicketCommentModel,
    ) -> ChamadosTicketCommentModel:
        """Adiciona um comentário à sessão."""

        self._session.add(comment)
        return comment

    def commit(
        self,
        comment: ChamadosTicketCommentModel,
    ) -> ChamadosTicketCommentModel:
        """Persiste e atualiza um comentário."""

        self._session.commit()
        self._session.refresh(comment)
        return comment