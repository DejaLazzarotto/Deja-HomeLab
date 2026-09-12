from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.chamados.client_users.repository import (
    ChamadosClientUserRepository,
)
from deja_indicadores_api.chamados.clients.repository import (
    ChamadosClientRepository,
)
from deja_indicadores_api.chamados.portal.service import (
    ChamadosPortalService,
)
from deja_indicadores_api.chamados.tickets.attachments.repository import (
    ChamadosTicketAttachmentRepository,
)
from deja_indicadores_api.chamados.tickets.comments.repository import (
    ChamadosTicketCommentRepository,
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
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


def get_chamados_portal_service(
    session: DatabaseSession,
) -> ChamadosPortalService:
    """Cria o serviço do Portal externo do Deja Chamados."""

    ticket_repository = ChamadosTicketRepository(session)
    user_repository = UserRepository(session)

    timeline_service = ChamadosTicketTimelineService(
        repository=ChamadosTicketTimelineRepository(session),
        ticket_repository=ticket_repository,
        authorization_service=AuthorizationService(),
        user_repository=user_repository,
    )

    return ChamadosPortalService(
        ticket_repository=ticket_repository,
        client_repository=ChamadosClientRepository(session),
        client_user_repository=ChamadosClientUserRepository(session),
        timeline_service=timeline_service,
        user_repository=user_repository,
        comment_repository=ChamadosTicketCommentRepository(session),
        attachment_repository=ChamadosTicketAttachmentRepository(session),
    )


ChamadosPortalServiceDependency = Annotated[
    ChamadosPortalService,
    Depends(get_chamados_portal_service),
]