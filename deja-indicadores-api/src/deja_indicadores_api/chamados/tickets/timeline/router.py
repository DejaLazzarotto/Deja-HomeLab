from typing import Annotated

from fastapi import APIRouter, Depends, Path

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.chamados.tickets.timeline.dependencies import (
    ChamadosTicketTimelineServiceDependency,
)
from deja_indicadores_api.chamados.tickets.timeline.schemas import (
    ChamadosTicketTimelineResponse,
)
from deja_indicadores_api.module_management.dependencies import require_module
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/chamados/tickets",
    tags=["Deja Chamados - Histórico"],
    dependencies=[Depends(require_module("chamados"))],
)

ChamadosTicketId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do chamado.",
    ),
]

ChamadosTicketReader = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
            UserRole.VIEWER,
        )
    ),
]


@router.get(
    "/{ticket_id}/timeline",
    response_model=list[ChamadosTicketTimelineResponse],
)
def list_ticket_timeline(
    ticket_id: ChamadosTicketId,
    service: ChamadosTicketTimelineServiceDependency,
    current_user: ChamadosTicketReader,
) -> list[ChamadosTicketTimelineResponse]:
    """Lista o histórico cronológico de um chamado autorizado."""

    return service.list_by_ticket_id(
        ticket_id,
        current_user,
    )
