from typing import Annotated

from fastapi import APIRouter, Depends, Path, status as http_status

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.chamados.tickets.comments.dependencies import (
    ChamadosTicketCommentServiceDependency,
)
from deja_indicadores_api.chamados.tickets.comments.schemas import (
    ChamadosTicketCommentCreate,
    ChamadosTicketCommentResponse,
)
from deja_indicadores_api.module_management.dependencies import require_module
from deja_indicadores_api.user_management.models import UserRole


router = APIRouter(
    prefix="/chamados/tickets",
    tags=["Deja Chamados - Comentários"],
    dependencies=[Depends(require_module("chamados"))],
)


TicketId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do chamado.",
    ),
]


ChamadosTicketCommentReader = Annotated[
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


ChamadosTicketCommentOperator = Annotated[
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
    "/{ticket_id}/comments",
    response_model=list[ChamadosTicketCommentResponse],
)
def list_ticket_comments(
    ticket_id: TicketId,
    service: ChamadosTicketCommentServiceDependency,
    current_user: ChamadosTicketCommentReader,
) -> list[ChamadosTicketCommentResponse]:
    """Lista os comentários de um chamado autorizado."""

    return service.list_by_ticket_id(
        ticket_id,
        current_user,
    )


@router.post(
    "/{ticket_id}/comments",
    response_model=ChamadosTicketCommentResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_ticket_comment(
    ticket_id: TicketId,
    input_data: ChamadosTicketCommentCreate,
    service: ChamadosTicketCommentServiceDependency,
    current_user: ChamadosTicketCommentOperator,
) -> ChamadosTicketCommentResponse:
    """Adiciona um comentário a um chamado autorizado."""

    return service.create(
        ticket_id,
        input_data,
        current_user,
    )