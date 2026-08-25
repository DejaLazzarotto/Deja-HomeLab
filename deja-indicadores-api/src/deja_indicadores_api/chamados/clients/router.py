from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Response,
    status,
)

from deja_indicadores_api.authentication.dependencies import (
    require_roles,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.chamados.clients.dependencies import (
    ChamadosClientServiceDependency,
)
from deja_indicadores_api.chamados.clients.schemas import (
    ChamadosClientCreate,
    ChamadosClientResponse,
    ChamadosClientUpdate,
)
from deja_indicadores_api.module_management.dependencies import (
    require_module,
)
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/chamados/clients",
    tags=["Deja Chamados - Clientes"],
    dependencies=[Depends(require_module("chamados"))],
)

ChamadosClientId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do cliente.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra clientes pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra clientes pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra clientes pelo ambiente.",
    ),
]

SearchFilter = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=255,
        description="Busca clientes pelos dados comerciais.",
    ),
]

ActiveFilter = Annotated[
    bool | None,
    Query(
        description="Filtra clientes pela situação.",
    ),
]

ChamadosClientReader = Annotated[
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

ChamadosClientManager = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
        )
    ),
]


@router.get(
    "",
    response_model=list[ChamadosClientResponse],
)
def list_clients(
    service: ChamadosClientServiceDependency,
    current_user: ChamadosClientReader,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
    search: SearchFilter = None,
    active: ActiveFilter = None,
) -> list[ChamadosClientResponse]:
    """Lista clientes dentro do escopo permitido."""

    return service.list(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        search=search,
        active=active,
    )


@router.get(
    "/{client_id}",
    response_model=ChamadosClientResponse,
)
def get_client(
    client_id: ChamadosClientId,
    service: ChamadosClientServiceDependency,
    current_user: ChamadosClientReader,
) -> ChamadosClientResponse:
    """Consulta um cliente dentro do escopo permitido."""

    return service.find_by_id(
        client_id,
        current_user,
    )


@router.post(
    "",
    response_model=ChamadosClientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    input_data: ChamadosClientCreate,
    service: ChamadosClientServiceDependency,
    current_user: ChamadosClientManager,
) -> ChamadosClientResponse:
    """Cadastra um cliente dentro do escopo permitido."""

    return service.create(
        input_data,
        current_user,
    )


@router.put(
    "/{client_id}",
    response_model=ChamadosClientResponse,
)
def update_client(
    client_id: ChamadosClientId,
    input_data: ChamadosClientUpdate,
    service: ChamadosClientServiceDependency,
    current_user: ChamadosClientManager,
) -> ChamadosClientResponse:
    """Atualiza integralmente um cliente autorizado."""

    return service.update(
        client_id,
        input_data,
        current_user,
    )


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_client(
    client_id: ChamadosClientId,
    service: ChamadosClientServiceDependency,
    current_user: ChamadosClientManager,
) -> Response:
    """Exclui um cliente dentro do escopo permitido."""

    service.delete(
        client_id,
        current_user,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
