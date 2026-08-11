from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from deja_indicadores_api.user_management.dependencies import (
    UserServiceDependency,
)
from deja_indicadores_api.user_management.models import UserStatus
from deja_indicadores_api.user_management.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(
    prefix="/v1",
    tags=["User Management"],
)


UserId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do usuário.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra usuários pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra usuários pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra usuários pelo ambiente.",
    ),
]

StatusFilter = Annotated[
    UserStatus | None,
    Query(description="Filtra usuários pelo status."),
]


@router.get(
    "/users",
    response_model=list[UserResponse],
)
def list_users(
    service: UserServiceDependency,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
    user_status: StatusFilter = None,
) -> list[UserResponse]:
    """Lista usuários com filtros institucionais opcionais."""

    return service.list(
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        status=user_status,
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UserId,
    service: UserServiceDependency,
) -> UserResponse:
    """Consulta um usuário pelo identificador."""

    return service.find_by_id(user_id)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    input_data: UserCreate,
    service: UserServiceDependency,
) -> UserResponse:
    """Cadastra um novo usuário institucional."""

    return service.create(input_data)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: UserId,
    input_data: UserUpdate,
    service: UserServiceDependency,
) -> UserResponse:
    """Atualiza integralmente ou desativa um usuário."""

    return service.update(user_id, input_data)