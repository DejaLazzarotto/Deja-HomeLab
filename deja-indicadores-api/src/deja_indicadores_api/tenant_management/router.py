from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.tenant_management.dependencies import (
    EnvironmentServiceDependency,
    OrganizationServiceDependency,
    TenantServiceDependency,
)
from deja_indicadores_api.tenant_management.schemas import (
    EnvironmentCreate,
    EnvironmentResponse,
    EnvironmentUpdate,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    TenantCreate,
    TenantResponse,
    TenantUpdate,
)
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/v1",
    tags=["Tenant Management"],
)

ResourceId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do recurso.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra recursos pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra recursos pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra recursos pelo ambiente.",
    ),
]

InstitutionalReader = Annotated[
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

EnvironmentReader = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.USER,
        )
    ),
]

PlatformAdministrator = Annotated[
    AuthenticatedUser,
    Depends(require_roles(UserRole.PLATFORM_ADMIN)),
]

OrganizationEditor = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
        )
    ),
]

TenantCreator = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
        )
    ),
]

TenantEditor = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
        )
    ),
]

EnvironmentAdministrator = Annotated[
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
    "/organizations",
    response_model=list[OrganizationResponse],
)
def list_organizations(
    service: OrganizationServiceDependency,
    current_user: InstitutionalReader,
    organization_id: OrganizationFilter = None,
) -> list[OrganizationResponse]:
    """Lista organizações dentro do escopo permitido."""

    return service.list(
        current_user,
        organization_id=organization_id,
    )


@router.get(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_id: ResourceId,
    service: OrganizationServiceDependency,
    current_user: InstitutionalReader,
) -> OrganizationResponse:
    """Consulta uma organização dentro do escopo permitido."""

    return service.find_by_id(organization_id, current_user)


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    input_data: OrganizationCreate,
    service: OrganizationServiceDependency,
    current_user: PlatformAdministrator,
) -> OrganizationResponse:
    """Cadastra uma nova organização por administração global."""

    return service.create(input_data, current_user)


@router.put(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
)
def update_organization(
    organization_id: ResourceId,
    input_data: OrganizationUpdate,
    service: OrganizationServiceDependency,
    current_user: OrganizationEditor,
) -> OrganizationResponse:
    """Atualiza uma organização dentro do escopo permitido."""

    return service.update(
        organization_id,
        input_data,
        current_user,
    )


@router.delete(
    "/organizations/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_organization(
    organization_id: ResourceId,
    service: OrganizationServiceDependency,
    current_user: PlatformAdministrator,
) -> Response:
    """Exclui uma organização por administração global."""

    service.delete(organization_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/tenants",
    response_model=list[TenantResponse],
)
def list_tenants(
    service: TenantServiceDependency,
    current_user: InstitutionalReader,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
) -> list[TenantResponse]:
    """Lista tenants dentro do escopo permitido."""

    return service.list(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
    )


@router.get(
    "/tenants/{tenant_id}",
    response_model=TenantResponse,
)
def get_tenant(
    tenant_id: ResourceId,
    service: TenantServiceDependency,
    current_user: InstitutionalReader,
) -> TenantResponse:
    """Consulta um tenant dentro do escopo permitido."""

    return service.find_by_id(tenant_id, current_user)


@router.post(
    "/tenants",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    input_data: TenantCreate,
    service: TenantServiceDependency,
    current_user: TenantCreator,
) -> TenantResponse:
    """Cadastra um tenant dentro do escopo permitido."""

    return service.create(input_data, current_user)


@router.put(
    "/tenants/{tenant_id}",
    response_model=TenantResponse,
)
def update_tenant(
    tenant_id: ResourceId,
    input_data: TenantUpdate,
    service: TenantServiceDependency,
    current_user: TenantEditor,
) -> TenantResponse:
    """Atualiza um tenant dentro do escopo permitido."""

    return service.update(
        tenant_id,
        input_data,
        current_user,
    )


@router.delete(
    "/tenants/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tenant(
    tenant_id: ResourceId,
    service: TenantServiceDependency,
    current_user: TenantCreator,
) -> Response:
    """Exclui um tenant dentro do escopo permitido."""

    service.delete(tenant_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/environments",
    response_model=list[EnvironmentResponse],
)
def list_environments(
    service: EnvironmentServiceDependency,
    current_user: EnvironmentReader,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
) -> list[EnvironmentResponse]:
    """Lista ambientes dentro do escopo permitido."""

    return service.list(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
    )


@router.get(
    "/environments/{environment_id}",
    response_model=EnvironmentResponse,
)
def get_environment(
    environment_id: ResourceId,
    service: EnvironmentServiceDependency,
    current_user: EnvironmentReader,
) -> EnvironmentResponse:
    """Consulta um ambiente dentro do escopo permitido."""

    return service.find_by_id(environment_id, current_user)


@router.post(
    "/environments",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_environment(
    input_data: EnvironmentCreate,
    service: EnvironmentServiceDependency,
    current_user: EnvironmentAdministrator,
) -> EnvironmentResponse:
    """Cadastra um ambiente dentro do escopo permitido."""

    return service.create(input_data, current_user)


@router.put(
    "/environments/{environment_id}",
    response_model=EnvironmentResponse,
)
def update_environment(
    environment_id: ResourceId,
    input_data: EnvironmentUpdate,
    service: EnvironmentServiceDependency,
    current_user: EnvironmentAdministrator,
) -> EnvironmentResponse:
    """Atualiza um ambiente dentro do escopo permitido."""

    return service.update(
        environment_id,
        input_data,
        current_user,
    )


@router.delete(
    "/environments/{environment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_environment(
    environment_id: ResourceId,
    service: EnvironmentServiceDependency,
    current_user: EnvironmentAdministrator,
) -> Response:
    """Exclui um ambiente dentro do escopo permitido."""

    service.delete(environment_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)