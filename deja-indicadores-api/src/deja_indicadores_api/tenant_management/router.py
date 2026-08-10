from typing import Annotated

from fastapi import APIRouter, Path, Response, status

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


@router.get(
    "/organizations",
    response_model=list[OrganizationResponse],
)
def list_organizations(
    service: OrganizationServiceDependency,
) -> list[OrganizationResponse]:
    """Lista todas as organizações cadastradas."""

    return service.list()


@router.get(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_id: ResourceId,
    service: OrganizationServiceDependency,
) -> OrganizationResponse:
    """Consulta uma organização pelo identificador."""

    return service.find_by_id(organization_id)


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    input_data: OrganizationCreate,
    service: OrganizationServiceDependency,
) -> OrganizationResponse:
    """Cadastra uma nova organização."""

    return service.create(input_data)


@router.put(
    "/organizations/{organization_id}",
    response_model=OrganizationResponse,
)
def update_organization(
    organization_id: ResourceId,
    input_data: OrganizationUpdate,
    service: OrganizationServiceDependency,
) -> OrganizationResponse:
    """Atualiza integralmente uma organização."""

    return service.update(organization_id, input_data)


@router.delete(
    "/organizations/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_organization(
    organization_id: ResourceId,
    service: OrganizationServiceDependency,
) -> Response:
    """Exclui uma organização."""

    service.delete(organization_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/tenants",
    response_model=list[TenantResponse],
)
def list_tenants(
    service: TenantServiceDependency,
) -> list[TenantResponse]:
    """Lista todos os tenants cadastrados."""

    return service.list()


@router.get(
    "/tenants/{tenant_id}",
    response_model=TenantResponse,
)
def get_tenant(
    tenant_id: ResourceId,
    service: TenantServiceDependency,
) -> TenantResponse:
    """Consulta um tenant pelo identificador."""

    return service.find_by_id(tenant_id)


@router.post(
    "/tenants",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    input_data: TenantCreate,
    service: TenantServiceDependency,
) -> TenantResponse:
    """Cadastra um novo tenant."""

    return service.create(input_data)


@router.put(
    "/tenants/{tenant_id}",
    response_model=TenantResponse,
)
def update_tenant(
    tenant_id: ResourceId,
    input_data: TenantUpdate,
    service: TenantServiceDependency,
) -> TenantResponse:
    """Atualiza integralmente um tenant."""

    return service.update(tenant_id, input_data)


@router.delete(
    "/tenants/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tenant(
    tenant_id: ResourceId,
    service: TenantServiceDependency,
) -> Response:
    """Exclui um tenant."""

    service.delete(tenant_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/environments",
    response_model=list[EnvironmentResponse],
)
def list_environments(
    service: EnvironmentServiceDependency,
) -> list[EnvironmentResponse]:
    """Lista todos os ambientes cadastrados."""

    return service.list()


@router.get(
    "/environments/{environment_id}",
    response_model=EnvironmentResponse,
)
def get_environment(
    environment_id: ResourceId,
    service: EnvironmentServiceDependency,
) -> EnvironmentResponse:
    """Consulta um ambiente pelo identificador."""

    return service.find_by_id(environment_id)


@router.post(
    "/environments",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_environment(
    input_data: EnvironmentCreate,
    service: EnvironmentServiceDependency,
) -> EnvironmentResponse:
    """Cadastra um novo ambiente."""

    return service.create(input_data)


@router.put(
    "/environments/{environment_id}",
    response_model=EnvironmentResponse,
)
def update_environment(
    environment_id: ResourceId,
    input_data: EnvironmentUpdate,
    service: EnvironmentServiceDependency,
) -> EnvironmentResponse:
    """Atualiza integralmente um ambiente."""

    return service.update(environment_id, input_data)


@router.delete(
    "/environments/{environment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_environment(
    environment_id: ResourceId,
    service: EnvironmentServiceDependency,
) -> Response:
    """Exclui um ambiente."""

    service.delete(environment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)