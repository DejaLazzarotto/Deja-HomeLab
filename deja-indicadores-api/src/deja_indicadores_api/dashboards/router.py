from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.dashboards.dependencies import (
    DashboardServiceDependency,
)
from deja_indicadores_api.dashboards.schemas import (
    DashboardOverviewResponse,
)
from deja_indicadores_api.module_management.dependencies import (
    require_module,
)
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/dashboards",
    tags=["Dashboards e Relatórios"],
    dependencies=[Depends(require_module("indicators"))],
)

CompanyIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o dashboard pelo UUID da empresa.",
    ),
]

IndicatorIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o dashboard pelo UUID do indicador.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o dashboard pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o dashboard pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o dashboard pelo ambiente.",
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

DashboardReader = Annotated[
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


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
)
def get_dashboard_overview(
    service: DashboardServiceDependency,
    current_user: DashboardReader,
    company_id: CompanyIdFilter = None,
    indicator_id: IndicatorIdFilter = None,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
    start_date: StartDateFilter = None,
    end_date: EndDateFilter = None,
) -> DashboardOverviewResponse:
    """Retorna a visão gerencial dentro do escopo permitido."""

    return service.get_overview(
        current_user,
        company_id=company_id,
        indicator_id=indicator_id,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        start_date=start_date,
        end_date=end_date,
    )