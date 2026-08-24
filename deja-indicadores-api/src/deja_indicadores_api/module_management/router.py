from typing import Annotated

from fastapi import APIRouter, Depends, Path

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.module_management.dependencies import (
    ModuleManagementServiceDependency,
)
from deja_indicadores_api.module_management.schemas import (
    ModuleResponse,
    OrganizationModulesResponse,
    OrganizationModulesUpdate,
)
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/v1",
    tags=["Module Management"],
)

OrganizationId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID da organização.",
    ),
]

PlatformAdministrator = Annotated[
    AuthenticatedUser,
    Depends(require_roles(UserRole.PLATFORM_ADMIN)),
]


@router.get(
    "/modules",
    response_model=list[ModuleResponse],
)
def list_modules(
    service: ModuleManagementServiceDependency,
    current_user: PlatformAdministrator,
) -> list[ModuleResponse]:
    """Lista o catálogo de módulos instalados."""

    return service.list_catalog(current_user)


@router.get(
    "/organizations/{organization_id}/modules",
    response_model=OrganizationModulesResponse,
)
def get_organization_modules(
    organization_id: OrganizationId,
    service: ModuleManagementServiceDependency,
    current_user: PlatformAdministrator,
) -> OrganizationModulesResponse:
    """Consulta o estado dos módulos de uma organização."""

    return service.get_organization_modules(
        organization_id,
        current_user,
    )


@router.put(
    "/organizations/{organization_id}/modules",
    response_model=OrganizationModulesResponse,
)
def update_organization_modules(
    organization_id: OrganizationId,
    input_data: OrganizationModulesUpdate,
    service: ModuleManagementServiceDependency,
    current_user: PlatformAdministrator,
) -> OrganizationModulesResponse:
    """Substitui os módulos liberados para uma organização."""

    return service.update_organization_modules(
        organization_id,
        input_data,
        current_user,
    )