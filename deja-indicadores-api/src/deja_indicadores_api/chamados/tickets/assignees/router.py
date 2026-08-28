from typing import Annotated

from fastapi import APIRouter, Depends, Query

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.chamados.tickets.assignees.dependencies import (
    ChamadosTicketAssigneeServiceDependency,
)
from deja_indicadores_api.chamados.tickets.assignees.schemas import (
    ChamadosTicketAssigneeResponse,
)
from deja_indicadores_api.module_management.dependencies import require_module
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/chamados/tickets",
    tags=["Deja Chamados - Responsáveis"],
    dependencies=[Depends(require_module("chamados"))],
)

ClientId = Annotated[
    str,
    Query(
        min_length=36,
        max_length=36,
        description="Cliente que define o escopo dos responsáveis.",
    ),
]

ChamadosTicketOperator = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
        )
    ),
]


@router.get(
    "/assignees",
    response_model=list[ChamadosTicketAssigneeResponse],
)
def list_ticket_assignees(
    client_id: ClientId,
    service: ChamadosTicketAssigneeServiceDependency,
    current_user: ChamadosTicketOperator,
) -> list[ChamadosTicketAssigneeResponse]:
    """Lista responsáveis elegíveis para o Cliente informado."""

    return service.list(
        client_id,
        current_user,
    )