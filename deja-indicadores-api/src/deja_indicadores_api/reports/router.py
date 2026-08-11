from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from deja_indicadores_api.reports.dependencies import (
    ReportServiceDependency,
)
from deja_indicadores_api.reports.schemas import (
    ManagementReportResponse,
)

router = APIRouter(prefix="/reports", tags=["Relatórios"])

CompanyIdFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra o relatório pelo UUID da empresa.",
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
    "/management",
    response_model=ManagementReportResponse,
)
def get_management_report(
    service: ReportServiceDependency,
    company_id: CompanyIdFilter = None,
    start_date: StartDateFilter = None,
    end_date: EndDateFilter = None,
) -> ManagementReportResponse:
    """Retorna o relatório gerencial básico dos indicadores."""

    return service.get_management_report(
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
    )