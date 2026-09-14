from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.chamados.tickets.comments.repository import (
    ChamadosTicketCommentRepository,
)
from deja_indicadores_api.chamados.tickets.comments.service import (
    ChamadosTicketCommentService,
)
from deja_indicadores_api.chamados.tickets.repository import (
    ChamadosTicketRepository,
)
from deja_indicadores_api.chamados.tickets.timeline.dependencies import (
    get_chamados_ticket_timeline_service,
)
from deja_indicadores_api.chamados.tickets.timeline.service import (
    ChamadosTicketTimelineService,
)
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]

TimelineServiceDependency = Annotated[
    ChamadosTicketTimelineService,
    Depends(get_chamados_ticket_timeline_service),
]


def get_chamados_ticket_comment_service(
    session: DatabaseSession,
    timeline_service: TimelineServiceDependency,
) -> ChamadosTicketCommentService:
    """Cria o serviço de comentários para a sessão da requisição."""

    return ChamadosTicketCommentService(
        ChamadosTicketCommentRepository(session),
        ChamadosTicketRepository(session),
        timeline_service,
        AuthorizationService(),
        UserRepository(session),
    )


ChamadosTicketCommentServiceDependency = Annotated[
    ChamadosTicketCommentService,
    Depends(get_chamados_ticket_comment_service),
]