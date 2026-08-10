from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.dashboards.repository import DashboardRepository
from deja_indicadores_api.dashboards.service import DashboardService


DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_dashboard_service(
    session: DatabaseSession,
) -> DashboardService:
    """Cria o serviço do dashboard para a sessão da requisição."""

    dashboard_repository = DashboardRepository(session)
    company_repository = CompanyRepository(session)

    return DashboardService(
        dashboard_repository,
        company_repository,
    )


DashboardServiceDependency = Annotated[
    DashboardService,
    Depends(get_dashboard_service),
]