from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.companies.service import CompanyService
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.indicators.repository import IndicatorRepository
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_company_service(session: DatabaseSession) -> CompanyService:
    """Cria o serviço de empresas para a sessão da requisição."""

    company_repository = CompanyRepository(session)
    indicator_repository = IndicatorRepository(session)
    tenant_repository = TenantRepository(session)
    environment_repository = EnvironmentRepository(session)
    authorization_service = AuthorizationService()

    return CompanyService(
        company_repository,
        indicator_repository,
        tenant_repository,
        environment_repository,
        authorization_service,
    )


CompanyServiceDependency = Annotated[
    CompanyService,
    Depends(get_company_service),
]
