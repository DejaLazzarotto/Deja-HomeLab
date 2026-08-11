from datetime import UTC, date, datetime

from deja_indicadores_api.dashboards.service import DashboardService
from deja_indicadores_api.reports.schemas import (
    ManagementReportFilters,
    ManagementReportResponse,
)


class ReportService:
    """Regras de aplicação dos relatórios gerenciais."""

    def __init__(self, dashboard_service: DashboardService) -> None:
        self._dashboard_service = dashboard_service

    def get_management_report(
        self,
        company_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> ManagementReportResponse:
        """Gera o relatório gerencial básico."""

        overview = self._dashboard_service.get_overview(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
        )

        return ManagementReportResponse(
            title="Relatório Gerencial de Indicadores",
            generated_at=datetime.now(UTC),
            filters=ManagementReportFilters(
                company_id=company_id,
                start_date=start_date,
                end_date=end_date,
            ),
            overview=overview,
        )