from datetime import date
from uuid import uuid4

from deja_indicadores_api.companies.exceptions import CompanyNotFoundError
from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.indicators.exceptions import IndicatorNotFoundError
from deja_indicadores_api.indicators.models import IndicatorModel
from deja_indicadores_api.indicators.repository import IndicatorRepository
from deja_indicadores_api.measurements.exceptions import (
    MeasurementAlreadyExistsError,
    MeasurementNotFoundError,
)
from deja_indicadores_api.measurements.models import MeasurementModel
from deja_indicadores_api.measurements.repository import MeasurementRepository
from deja_indicadores_api.measurements.schemas import (
    MeasurementCreate,
    MeasurementUpdate,
)


class MeasurementService:
    """Regras de aplicação da Coleta Manual de Dados."""

    def __init__(
        self,
        repository: MeasurementRepository,
        indicator_repository: IndicatorRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self._repository = repository
        self._indicator_repository = indicator_repository
        self._company_repository = company_repository

    def list(
        self,
        company_id: str | None = None,
        indicator_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MeasurementModel]:
        """Lista medições de acordo com os filtros informados."""

        if company_id is not None:
            self._ensure_company_exists(company_id)

        if indicator_id is not None:
            indicator = self._find_indicator(indicator_id)

            if company_id is not None and indicator.company_id != company_id:
                return []

        return self._repository.list(
            company_id=company_id,
            indicator_id=indicator_id,
            start_date=start_date,
            end_date=end_date,
        )

    def find_by_id(self, measurement_id: str) -> MeasurementModel:
        """Retorna uma medição pelo identificador."""

        measurement = self._repository.find_by_id(measurement_id)

        if measurement is None:
            raise MeasurementNotFoundError(measurement_id)

        return measurement

    def create(
        self,
        input_data: MeasurementCreate,
    ) -> MeasurementModel:
        """Cadastra uma nova medição manual."""

        self._find_indicator(input_data.indicator_id)
        self._ensure_period_is_available(
            input_data.indicator_id,
            input_data.reference_date,
        )

        measurement = MeasurementModel(
            id=str(uuid4()),
            created_by=None,
            **input_data.model_dump(),
        )

        return self._repository.add(measurement)

    def update(
        self,
        measurement_id: str,
        input_data: MeasurementUpdate,
    ) -> MeasurementModel:
        """Atualiza integralmente uma medição existente."""

        measurement = self.find_by_id(measurement_id)

        self._find_indicator(input_data.indicator_id)
        self._ensure_period_is_available(
            input_data.indicator_id,
            input_data.reference_date,
            ignored_measurement_id=measurement_id,
        )

        for field_name, value in input_data.model_dump().items():
            setattr(measurement, field_name, value)

        return self._repository.update(measurement)

    def delete(self, measurement_id: str) -> None:
        """Exclui uma medição existente."""

        measurement = self.find_by_id(measurement_id)
        self._repository.delete(measurement)

    def _ensure_company_exists(self, company_id: str) -> None:
        """Garante que a empresa informada esteja cadastrada."""

        company = self._company_repository.find_by_id(company_id)

        if company is None:
            raise CompanyNotFoundError(company_id)

    def _find_indicator(self, indicator_id: str) -> IndicatorModel:
        """Localiza e retorna o indicador informado."""

        indicator = self._indicator_repository.find_by_id(indicator_id)

        if indicator is None:
            raise IndicatorNotFoundError(indicator_id)

        return indicator

    def _ensure_period_is_available(
        self,
        indicator_id: str,
        reference_date: date,
        ignored_measurement_id: str | None = None,
    ) -> None:
        """Garante uma única medição por indicador e data."""

        existing_measurement = (
            self._repository.find_by_indicator_and_reference_date(
                indicator_id,
                reference_date,
            )
        )

        if (
            existing_measurement is not None
            and existing_measurement.id != ignored_measurement_id
        ):
            raise MeasurementAlreadyExistsError(
                indicator_id,
                reference_date.isoformat(),
            )