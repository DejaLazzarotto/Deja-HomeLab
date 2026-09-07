from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.chamados.tickets.timeline.models import (
    ChamadosTicketTimelineModel,
)


class ChamadosTicketTimelineRepository:
    """Acesso persistente ao histórico dos chamados."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def list_by_ticket_id(
        self,
        ticket_id: str,
    ) -> list[ChamadosTicketTimelineModel]:
        """Lista os eventos de um chamado em ordem cronológica."""

        statement = (
            select(ChamadosTicketTimelineModel)
            .where(
                ChamadosTicketTimelineModel.ticket_id == ticket_id
            )
            .order_by(
                ChamadosTicketTimelineModel.created_at.asc(),
                ChamadosTicketTimelineModel.id.asc(),
            )
        )

        return list(self._session.scalars(statement).all())

    def add(
        self,
        timeline: ChamadosTicketTimelineModel,
    ) -> ChamadosTicketTimelineModel:
        """Adiciona um evento ao histórico sem finalizar a transação."""

        self._session.add(timeline)
        self._session.flush()
        return timeline
