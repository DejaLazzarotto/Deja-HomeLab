from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.companies.service import CompanyService
from deja_indicadores_api.core.database import get_db_session

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_company_service(session: DatabaseSession) -> CompanyService:
    """Cria o serviço de empresas para a sessão da requisição."""

    repository = CompanyRepository(session)
    return CompanyService(repository)


CompanyServiceDependency = Annotated[
    CompanyService,
    Depends(get_company_service),
]
