from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.measurements.dependencies import (
    MeasurementServiceDependency,
)
from deja_indicadores_api.measurements.schemas import (
    MeasurementCreate,
    MeasurementResponse,
    MeasurementUpdate,
)
from deja_indicadores_api.module_management.dependencies import (
    require_module,
)
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/measurements",
    tags=["Coleta Manual de Dados"],
    dependencies=[Depends(require_module("measurements"))],
)

MeasurementId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID da medição.",
    ),
]

CompanyIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra as medições pelo UUID da empresa.",
    ),
]

IndicatorIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra as medições pelo UUID do indicador.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra medições pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra medições pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra medições pelo ambiente.",
    ),
]

StartDateFilter = Annotated[
    date | None,
    Query(
        description="Data inicial inclusiva do período de referência.",
    ),
]

EndDateFilter = Annotated[
    date | None,
    Query(
        description="Data final inclusiva do período de referência.",
    ),
]

MeasurementReader = Annotated[
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

MeasurementEditor = Annotated[
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


@router.get("", response_model=list[MeasurementResponse])
def list_measurements(
    service: MeasurementServiceDependency,
    current_user: MeasurementReader,
    company_id: CompanyIdFilter = None,
    indicator_id: IndicatorIdFilter = None,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
    start_date: StartDateFilter = None,
    end_date: EndDateFilter = None,
) -> list[MeasurementResponse]:
    """Lista medições dentro do escopo permitido."""

    return service.list(
        current_user,
        company_id=company_id,
        indicator_id=indicator_id,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{measurement_id}", response_model=MeasurementResponse)
def get_measurement(
    measurement_id: MeasurementId,
    service: MeasurementServiceDependency,
    current_user: MeasurementReader,
) -> MeasurementResponse:
    """Consulta uma medição dentro do escopo permitido."""

    return service.find_by_id(measurement_id, current_user)


@router.post(
    "",
    response_model=MeasurementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_measurement(
    input_data: MeasurementCreate,
    service: MeasurementServiceDependency,
    current_user: MeasurementEditor,
) -> MeasurementResponse:
    """Cadastra uma medição manual dentro do escopo permitido."""

    return service.create(input_data, current_user)


@router.put(
    "/{measurement_id}",
    response_model=MeasurementResponse,
)
def update_measurement(
    measurement_id: MeasurementId,
    input_data: MeasurementUpdate,
    service: MeasurementServiceDependency,
    current_user: MeasurementEditor,
) -> MeasurementResponse:
    """Atualiza integralmente uma medição dentro do escopo permitido."""

    return service.update(
        measurement_id,
        input_data,
        current_user,
    )


@router.delete(
    "/{measurement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_measurement(
    measurement_id: MeasurementId,
    service: MeasurementServiceDependency,
    current_user: MeasurementEditor,
) -> Response:
    """Exclui uma medição operacional dentro do escopo permitido."""

    service.delete(measurement_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)