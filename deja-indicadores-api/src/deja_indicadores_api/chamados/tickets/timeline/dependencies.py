from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.chamados.tickets.repository import (
    ChamadosTicketRepository,
)
from deja_indicadores_api.chamados.tickets.timeline.repository import (
    ChamadosTicketTimelineRepository,
)
from deja_indicadores_api.chamados.tickets.timeline.service import (
    ChamadosTicketTimelineService,
)
from deja_indicadores_api.core.database import get_db_session

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


def get_chamados_ticket_timeline_service(
    session: DatabaseSession,
) -> ChamadosTicketTimelineService:
    """Cria o serviço de timeline para a sessão da requisição."""

    return ChamadosTicketTimelineService(
        ChamadosTicketTimelineRepository(session),
        ChamadosTicketRepository(session),
        AuthorizationService(),
    )


ChamadosTicketTimelineServiceDependency = Annotated[
    ChamadosTicketTimelineService,
    Depends(get_chamados_ticket_timeline_service),
]
