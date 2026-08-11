from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.indicators.repository import IndicatorRepository
from deja_indicadores_api.measurements.repository import MeasurementRepository
from deja_indicadores_api.measurements.service import MeasurementService

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_measurement_service(
    session: DatabaseSession,
) -> MeasurementService:
    """Cria o serviço de medições para a sessão da requisição."""

    measurement_repository = MeasurementRepository(session)
    indicator_repository = IndicatorRepository(session)
    company_repository = CompanyRepository(session)

    return MeasurementService(
        measurement_repository,
        indicator_repository,
        company_repository,
    )


MeasurementServiceDependency = Annotated[
    MeasurementService,
    Depends(get_measurement_service),
]