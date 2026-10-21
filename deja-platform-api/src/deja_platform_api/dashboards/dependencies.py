from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_platform_api.authentication.authorization import (
    AuthorizationService,
)
from deja_platform_api.companies.repository import CompanyRepository
from deja_platform_api.core.database import get_db_session
from deja_platform_api.dashboards.repository import DashboardRepository
from deja_platform_api.dashboards.service import DashboardService
from deja_platform_api.indicators.repository import IndicatorRepository
from deja_platform_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_dashboard_service(
    session: DatabaseSession,
) -> DashboardService:
    """Cria o serviço do dashboard para a sessão da requisição."""

    dashboard_repository = DashboardRepository(session)
    company_repository = CompanyRepository(session)
    indicator_repository = IndicatorRepository(session)
    tenant_repository = TenantRepository(session)
    environment_repository = EnvironmentRepository(session)
    authorization_service = AuthorizationService()

    return DashboardService(
        dashboard_repository,
        company_repository,
        indicator_repository,
        tenant_repository,
        environment_repository,
        authorization_service,
    )


DashboardServiceDependency = Annotated[
    DashboardService,
    Depends(get_dashboard_service),
]