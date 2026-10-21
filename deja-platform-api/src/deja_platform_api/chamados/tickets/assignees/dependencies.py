from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_platform_api.authentication.authorization import (
    AuthorizationService,
)
from deja_platform_api.chamados.clients.repository import (
    ChamadosClientRepository,
)
from deja_platform_api.chamados.tickets.assignees.service import (
    ChamadosTicketAssigneeService,
)
from deja_platform_api.core.database import get_db_session
from deja_platform_api.user_management.repository import UserRepository

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


def get_chamados_ticket_assignee_service(
    session: DatabaseSession,
) -> ChamadosTicketAssigneeService:
    """Cria o serviço de responsáveis para a sessão da requisição."""

    return ChamadosTicketAssigneeService(
        ChamadosClientRepository(session),
        UserRepository(session),
        AuthorizationService(),
    )


ChamadosTicketAssigneeServiceDependency = Annotated[
    ChamadosTicketAssigneeService,
    Depends(get_chamados_ticket_assignee_service),
]