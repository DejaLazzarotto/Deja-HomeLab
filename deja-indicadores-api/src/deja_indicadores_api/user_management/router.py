from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.user_management.dependencies import (
    UserServiceDependency,
)
from deja_indicadores_api.user_management.models import (
    UserRole,
    UserStatus,
)
from deja_indicadores_api.user_management.schemas import (
    UserCreate,
    UserModuleAccessesResponse,
    UserModuleAccessUpdate,
    UserPasswordSet,
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
    Query(
        description="Filtra usuários pelo status.",
    ),
]

UserAdministrator = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
        )
    ),
]


@router.get(
    "/users",
    response_model=list[UserResponse],
)
def list_users(
    service: UserServiceDependency,
    current_user: UserAdministrator,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
    user_status: StatusFilter = None,
) -> list[UserResponse]:
    """Lista usuários dentro do escopo do administrador."""

    return service.list(
        current_user,
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
    current_user: UserAdministrator,
) -> UserResponse:
    """Consulta um usuário permitido pelo escopo do administrador."""

    return service.find_by_id(
        user_id,
        current_user,
    )


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    input_data: UserCreate,
    service: UserServiceDependency,
    current_user: UserAdministrator,
) -> UserResponse:
    """Cadastra um usuário dentro do escopo do administrador."""

    return service.create(
        input_data,
        current_user,
    )


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: UserId,
    input_data: UserUpdate,
    service: UserServiceDependency,
    current_user: UserAdministrator,
) -> UserResponse:
    """Atualiza um usuário dentro do escopo do administrador."""

    return service.update(
        user_id,
        input_data,
        current_user,
    )


@router.put(
    "/users/{user_id}/password",
    response_model=UserResponse,
)
def set_user_password(
    user_id: UserId,
    input_data: UserPasswordSet,
    service: UserServiceDependency,
    current_user: UserAdministrator,
) -> UserResponse:
    """Define a senha de um usuário permitido pelo escopo."""

    return service.set_password(
        user_id,
        input_data,
        current_user,
    )


@router.get(
    "/users/{user_id}/modules",
    response_model=UserModuleAccessesResponse,
)
def get_user_module_accesses(
    user_id: UserId,
    service: UserServiceDependency,
    current_user: UserAdministrator,
) -> UserModuleAccessesResponse:
    """Consulta os acessos funcionais do usuário por módulo."""

    return service.get_module_accesses(
        user_id,
        current_user,
    )


@router.put(
    "/users/{user_id}/modules",
    response_model=UserModuleAccessesResponse,
)
def update_user_module_accesses(
    user_id: UserId,
    input_data: UserModuleAccessUpdate,
    service: UserServiceDependency,
    current_user: UserAdministrator,
) -> UserModuleAccessesResponse:
    """Substitui os acessos funcionais do usuário por módulo."""

    return service.update_module_accesses(
        user_id,
        input_data,
        current_user,
    )