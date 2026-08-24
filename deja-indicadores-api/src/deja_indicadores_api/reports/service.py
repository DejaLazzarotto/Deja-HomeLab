from datetime import UTC, date, datetime

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.dashboards.service import DashboardService
from deja_indicadores_api.reports.schemas import (
    ManagementReportFilters,
    ManagementReportResponse,
)
from deja_indicadores_api.user_management.models import UserRole

REPORT_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)


class ReportService:
    """Regras de aplicação dos relatórios gerenciais."""

    def __init__(
        self,
        dashboard_service: DashboardService,
        authorization_service: AuthorizationService,
    ) -> None:
        self._dashboard_service = dashboard_service
        self._authorization_service = authorization_service

    def get_management_report(
        self,
        current_user: AuthenticatedUser,
        *,
        company_id: str | None = None,
        indicator_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> ManagementReportResponse:
        """Gera o relatório gerencial dentro do escopo permitido."""

        self._authorization_service.require_roles(
            current_user,
            REPORT_READER_ROLES,
        )
        self._authorization_service.require_module(
            current_user,
            "reports",
        )

        overview = self._dashboard_service.get_overview(
            current_user,
            company_id=company_id,
            indicator_id=indicator_id,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
            start_date=start_date,
            end_date=end_date,
        )

        return ManagementReportResponse(
            title="Relatório Gerencial de Indicadores",
            generated_at=datetime.now(UTC),
            filters=ManagementReportFilters(
                company_id=company_id,
                indicator_id=indicator_id,
                organization_id=organization_id,
                tenant_id=tenant_id,
                environment_id=environment_id,
                start_date=start_date,
                end_date=end_date,
            ),
            overview=overview,
        )