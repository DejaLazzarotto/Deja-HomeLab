from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from deja_indicadores_api.dashboards.dependencies import (
    DashboardServiceDependency,
)
from deja_indicadores_api.dashboards.schemas import (
    DashboardOverviewResponse,
)


router = APIRouter(prefix="/dashboards", tags=["Dashboards e Relatórios"])


CompanyIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o dashboard pelo UUID da empresa.",
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


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
)
def get_dashboard_overview(
    service: DashboardServiceDependency,
    company_id: CompanyIdFilter = None,
    start_date: StartDateFilter = None,
    end_date: EndDateFilter = None,
) -> DashboardOverviewResponse:
    """Retorna a visão gerencial consolidada dos indicadores."""

    return service.get_overview(
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
    )