from uuid import uuid4

from deja_indicadores_api.companies.exceptions import CompanyNotFoundError
from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.indicators.exceptions import (
    IndicatorNameAlreadyExistsError,
    IndicatorNotFoundError,
)
from deja_indicadores_api.indicators.models import IndicatorModel
from deja_indicadores_api.indicators.repository import IndicatorRepository
from deja_indicadores_api.indicators.schemas import (
    IndicatorCreate,
    IndicatorUpdate,
)


class IndicatorService:
    """Regras de aplicação da Gestão de Indicadores."""

    def __init__(
        self,
        repository: IndicatorRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self._repository = repository
        self._company_repository = company_repository

    def list(
        self,
        company_id: str | None = None,
    ) -> list[IndicatorModel]:
        """Lista indicadores, opcionalmente filtrados por empresa."""

        if company_id is not None:
            self._ensure_company_exists(company_id)

        return self._repository.list(company_id)

    def find_by_id(self, indicator_id: str) -> IndicatorModel:
        """Retorna um indicador pelo identificador."""

        indicator = self._repository.find_by_id(indicator_id)

        if indicator is None:
            raise IndicatorNotFoundError(indicator_id)

        return indicator

    def create(self, input_data: IndicatorCreate) -> IndicatorModel:
        """Cadastra um novo indicador."""

        self._ensure_company_exists(input_data.company_id)
        self._ensure_name_is_available(
            input_data.company_id,
            input_data.name,
        )

        indicator = IndicatorModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._repository.add(indicator)

    def update(
        self,
        indicator_id: str,
        input_data: IndicatorUpdate,
    ) -> IndicatorModel:
        """Atualiza integralmente um indicador existente."""

        indicator = self.find_by_id(indicator_id)

        self._ensure_company_exists(input_data.company_id)
        self._ensure_name_is_available(
            input_data.company_id,
            input_data.name,
            ignored_indicator_id=indicator_id,
        )

        for field_name, value in input_data.model_dump().items():
            setattr(indicator, field_name, value)

        return self._repository.update(indicator)

    def delete(self, indicator_id: str) -> None:
        """Exclui um indicador existente."""

        indicator = self.find_by_id(indicator_id)
        self._repository.delete(indicator)

    def _ensure_company_exists(self, company_id: str) -> None:
        """Garante que a empresa informada esteja cadastrada."""

        company = self._company_repository.find_by_id(company_id)

        if company is None:
            raise CompanyNotFoundError(company_id)

    def _ensure_name_is_available(
        self,
        company_id: str,
        name: str,
        ignored_indicator_id: str | None = None,
    ) -> None:
        """Garante a unicidade do nome do indicador na empresa."""

        existing_indicator = self._repository.find_by_company_and_name(
            company_id,
            name,
        )

        if (
            existing_indicator is not None
            and existing_indicator.id != ignored_indicator_id
        ):
            raise IndicatorNameAlreadyExistsError(company_id, name)