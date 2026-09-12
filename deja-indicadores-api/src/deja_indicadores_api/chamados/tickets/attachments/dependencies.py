from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.chamados.tickets.attachments.repository import (
    ChamadosTicketAttachmentRepository,
)
from deja_indicadores_api.chamados.tickets.attachments.service import (
    ChamadosTicketAttachmentService,
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
from deja_indicadores_api.core.config import Settings, get_settings
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]

SettingsDependency = Annotated[
    Settings,
    Depends(get_settings),
]

TimelineServiceDependency = Annotated[
    ChamadosTicketTimelineService,
    Depends(get_chamados_ticket_timeline_service),
]


def get_chamados_ticket_attachment_service(
    session: DatabaseSession,
    timeline_service: TimelineServiceDependency,
    settings: SettingsDependency,
) -> ChamadosTicketAttachmentService:
    """Cria o serviço de anexos para a sessão da requisição."""

    return ChamadosTicketAttachmentService(
        ChamadosTicketAttachmentRepository(session),
        ChamadosTicketRepository(session),
        timeline_service,
        AuthorizationService(),
        UserRepository(session),
        settings,
    )


ChamadosTicketAttachmentServiceDependency = Annotated[
    ChamadosTicketAttachmentService,
    Depends(get_chamados_ticket_attachment_service),
]