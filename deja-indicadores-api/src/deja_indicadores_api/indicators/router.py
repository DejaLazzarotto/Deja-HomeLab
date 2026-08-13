from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.indicators.dependencies import (
    IndicatorServiceDependency,
)
from deja_indicadores_api.indicators.schemas import (
    IndicatorCreate,
    IndicatorResponse,
    IndicatorUpdate,
)
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(prefix="/indicators", tags=["Indicadores"])

IndicatorId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do indicador.",
    ),
]

CompanyIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra os indicadores pelo UUID da empresa.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra indicadores pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra indicadores pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra indicadores pelo ambiente.",
    ),
]

IndicatorReader = Annotated[
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

IndicatorEditor = Annotated[
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

IndicatorManager = Annotated[
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


@router.get("", response_model=list[IndicatorResponse])
def list_indicators(
    service: IndicatorServiceDependency,
    current_user: IndicatorReader,
    company_id: CompanyIdFilter = None,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
) -> list[IndicatorResponse]:
    """Lista indicadores dentro do escopo permitido."""

    return service.list(
        current_user,
        company_id=company_id,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
    )


@router.get("/{indicator_id}", response_model=IndicatorResponse)
def get_indicator(
    indicator_id: IndicatorId,
    service: IndicatorServiceDependency,
    current_user: IndicatorReader,
) -> IndicatorResponse:
    """Consulta um indicador dentro do escopo permitido."""

    return service.find_by_id(indicator_id, current_user)


@router.post(
    "",
    response_model=IndicatorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_indicator(
    input_data: IndicatorCreate,
    service: IndicatorServiceDependency,
    current_user: IndicatorEditor,
) -> IndicatorResponse:
    """Cadastra um indicador dentro do escopo permitido."""

    return service.create(input_data, current_user)


@router.put("/{indicator_id}", response_model=IndicatorResponse)
def update_indicator(
    indicator_id: IndicatorId,
    input_data: IndicatorUpdate,
    service: IndicatorServiceDependency,
    current_user: IndicatorEditor,
) -> IndicatorResponse:
    """Atualiza integralmente um indicador dentro do escopo permitido."""

    return service.update(
        indicator_id,
        input_data,
        current_user,
    )


@router.delete(
    "/{indicator_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_indicator(
    indicator_id: IndicatorId,
    service: IndicatorServiceDependency,
    current_user: IndicatorManager,
) -> Response:
    """Exclui um indicador dentro do escopo permitido."""

    service.delete(indicator_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)