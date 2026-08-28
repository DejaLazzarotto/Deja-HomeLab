from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.chamados.clients.repository import (
    ChamadosClientRepository,
)
from deja_indicadores_api.chamados.tickets.repository import (
    ChamadosTicketRepository,
)
from deja_indicadores_api.chamados.tickets.service import (
    ChamadosTicketService,
)
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


def get_chamados_ticket_service(
    session: DatabaseSession,
) -> ChamadosTicketService:
    """Cria o serviço de chamados para a sessão da requisição."""

    return ChamadosTicketService(
        ChamadosTicketRepository(session),
        ChamadosClientRepository(session),
        UserRepository(session),
        AuthorizationService(),
    )


ChamadosTicketServiceDependency = Annotated[
    ChamadosTicketService,
    Depends(get_chamados_ticket_service),
]