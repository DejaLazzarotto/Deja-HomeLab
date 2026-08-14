from datetime import date, datetime

from pydantic import BaseModel

from deja_indicadores_api.dashboards.schemas import (
    DashboardOverviewResponse,
)


class ManagementReportFilters(BaseModel):
    """Filtros efetivamente solicitados para o relatório gerencial."""

    company_id: str | None
    indicator_id: str | None
    organization_id: str | None
    tenant_id: str | None
    environment_id: str | None
    start_date: date | None
    end_date: date | None


class ManagementReportResponse(BaseModel):
    """Representação do relatório gerencial básico."""

    title: str
    generated_at: datetime
    filters: ManagementReportFilters
    overview: DashboardOverviewResponse