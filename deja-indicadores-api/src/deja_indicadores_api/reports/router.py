from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.module_management.dependencies import (
    require_module,
)
from deja_indicadores_api.reports.dependencies import (
    ReportServiceDependency,
)
from deja_indicadores_api.reports.schemas import (
    ManagementReportResponse,
)
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/reports",
    tags=["Relatórios"],
    dependencies=[Depends(require_module("reports"))],
)

CompanyIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o relatório pelo UUID da empresa.",
    ),
]

IndicatorIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o relatório pelo UUID do indicador.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o relatório pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o relatório pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o relatório pelo ambiente.",
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

ReportReader = Annotated[
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
    "/management",
    response_model=ManagementReportResponse,
)
def get_management_report(
    service: ReportServiceDependency,
    current_user: ReportReader,
    company_id: CompanyIdFilter = None,
    indicator_id: IndicatorIdFilter = None,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
    start_date: StartDateFilter = None,
    end_date: EndDateFilter = None,
) -> ManagementReportResponse:
    """Retorna o relatório gerencial dentro do escopo permitido."""

    return service.get_management_report(
        current_user,
        company_id=company_id,
        indicator_id=indicator_id,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        start_date=start_date,
        end_date=end_date,
    )