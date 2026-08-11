from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.indicators.repository import IndicatorRepository
from deja_indicadores_api.indicators.service import IndicatorService
from deja_indicadores_api.measurements.repository import MeasurementRepository

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_indicator_service(
    session: DatabaseSession,
) -> IndicatorService:
    """Cria o serviço de indicadores para a sessão da requisição."""

    indicator_repository = IndicatorRepository(session)
    company_repository = CompanyRepository(session)
    measurement_repository = MeasurementRepository(session)

    return IndicatorService(
        indicator_repository,
        company_repository,
        measurement_repository,
    )


IndicatorServiceDependency = Annotated[
    IndicatorService,
    Depends(get_indicator_service),
]