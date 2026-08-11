from typing import Annotated

from fastapi import Depends

from deja_indicadores_api.dashboards.dependencies import (
    DashboardServiceDependency,
)
from deja_indicadores_api.reports.service import ReportService


def get_report_service(
    dashboard_service: DashboardServiceDependency,
) -> ReportService:
    """Cria o serviço de relatórios para a requisição."""

    return ReportService(dashboard_service)


ReportServiceDependency = Annotated[
    ReportService,
    Depends(get_report_service),
]