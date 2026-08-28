from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status as http_status

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.chamados.tickets.dependencies import (
    ChamadosTicketServiceDependency,
)
from deja_indicadores_api.chamados.tickets.enums import (
    ChamadosTicketPriority,
    ChamadosTicketStatus,
)
from deja_indicadores_api.chamados.tickets.schemas import (
    ChamadosTicketCreate,
    ChamadosTicketResponse,
    ChamadosTicketStatusUpdate,
    ChamadosTicketUpdate,
)
from deja_indicadores_api.module_management.dependencies import require_module
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/chamados/tickets",
    tags=["Deja Chamados - Chamados"],
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

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra chamados pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra chamados pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra chamados pelo ambiente.",
    ),
]

ClientFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra chamados pelo Cliente.",
    ),
]

AssignedUserFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra chamados pelo responsável.",
    ),
]

StatusFilter = Annotated[
    ChamadosTicketStatus | None,
    Query(
        alias="status",
        description="Filtra chamados pelo estado.",
    ),
]

PriorityFilter = Annotated[
    ChamadosTicketPriority | None,
    Query(
        alias="priority",
        description="Filtra chamados pela prioridade.",
    ),
]

SearchFilter = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=255,
        description="Busca chamados pelo título ou descrição.",
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
    "",
    response_model=list[ChamadosTicketResponse],
)
def list_tickets(
    service: ChamadosTicketServiceDependency,
    current_user: ChamadosTicketReader,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
    client_id: ClientFilter = None,
    ticket_status: StatusFilter = None,
    priority: PriorityFilter = None,
    assigned_to_user_id: AssignedUserFilter = None,
    search: SearchFilter = None,
) -> list[ChamadosTicketResponse]:
    """Lista chamados dentro do escopo permitido."""

    return service.list(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        client_id=client_id,
        status=ticket_status,
        priority=priority,
        assigned_to_user_id=assigned_to_user_id,
        search=search,
    )


@router.get(
    "/{ticket_id}",
    response_model=ChamadosTicketResponse,
)
def get_ticket(
    ticket_id: ChamadosTicketId,
    service: ChamadosTicketServiceDependency,
    current_user: ChamadosTicketReader,
) -> ChamadosTicketResponse:
    """Consulta um chamado dentro do escopo permitido."""

    return service.find_by_id(ticket_id, current_user)


@router.post(
    "",
    response_model=ChamadosTicketResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_ticket(
    input_data: ChamadosTicketCreate,
    service: ChamadosTicketServiceDependency,
    current_user: ChamadosTicketOperator,
) -> ChamadosTicketResponse:
    """Abre um chamado dentro do escopo permitido."""

    return service.create(input_data, current_user)


@router.put(
    "/{ticket_id}",
    response_model=ChamadosTicketResponse,
)
def update_ticket(
    ticket_id: ChamadosTicketId,
    input_data: ChamadosTicketUpdate,
    service: ChamadosTicketServiceDependency,
    current_user: ChamadosTicketOperator,
) -> ChamadosTicketResponse:
    """Atualiza os dados operacionais de um chamado autorizado."""

    return service.update(ticket_id, input_data, current_user)


@router.patch(
    "/{ticket_id}/status",
    response_model=ChamadosTicketResponse,
)
def update_ticket_status(
    ticket_id: ChamadosTicketId,
    input_data: ChamadosTicketStatusUpdate,
    service: ChamadosTicketServiceDependency,
    current_user: ChamadosTicketOperator,
) -> ChamadosTicketResponse:
    """Altera o estado de um chamado autorizado."""

    return service.update_status(ticket_id, input_data, current_user)