from datetime import date
from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.companies.exceptions import CompanyNotFoundError
from deja_indicadores_api.companies.models import CompanyModel
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
from deja_indicadores_api.tenant_management.exceptions import (
    EnvironmentNotFoundError,
    TenantNotFoundError,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    TenantModel,
)
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)
from deja_indicadores_api.user_management.models import UserRole

MEASUREMENT_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)

MEASUREMENT_EDITOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
    }
)


class MeasurementService:
    """Regras de aplicação da Coleta Manual de Dados."""

    def __init__(
        self,
        repository: MeasurementRepository,
        indicator_repository: IndicatorRepository,
        company_repository: CompanyRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._indicator_repository = indicator_repository
        self._company_repository = company_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._authorization_service = authorization_service

    def list(
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
    ) -> list[MeasurementModel]:
        """Lista medições dentro do escopo permitido."""

        self._require_roles(current_user, MEASUREMENT_READER_ROLES)

        if company_id is not None:
            company = self._require_company(company_id)
            self._require_company_scope(current_user, company)

        if indicator_id is not None:
            indicator = self._require_indicator(indicator_id)
            indicator_company = self._require_company(
                indicator.company_id
            )
            self._require_company_scope(
                current_user,
                indicator_company,
            )

            if (
                company_id is not None
                and indicator.company_id != company_id
            ):
                return []

        (
            effective_organization_id,
            effective_tenant_id,
            effective_environment_id,
        ) = self._authorization_service.resolve_list_scope(
            current_user,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )

        return self._repository.list(
            company_id=company_id,
            indicator_id=indicator_id,
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
            start_date=start_date,
            end_date=end_date,
        )

    def find_by_id(
        self,
        measurement_id: str,
        current_user: AuthenticatedUser,
    ) -> MeasurementModel:
        """Retorna uma medição dentro do escopo permitido."""

        self._require_roles(current_user, MEASUREMENT_READER_ROLES)
        measurement = self._find_by_id(measurement_id)
        indicator = self._require_indicator(measurement.indicator_id)
        company = self._require_company(indicator.company_id)
        self._require_company_scope(current_user, company)

        return measurement

    def create(
        self,
        input_data: MeasurementCreate,
        current_user: AuthenticatedUser,
    ) -> MeasurementModel:
        """Cadastra uma medição manual dentro do escopo permitido."""

        self._require_roles(current_user, MEASUREMENT_EDITOR_ROLES)
        indicator = self._require_indicator(input_data.indicator_id)
        company = self._require_company(indicator.company_id)
        self._require_company_scope(current_user, company)
        self._ensure_period_is_available(
            input_data.indicator_id,
            input_data.reference_date,
        )

        measurement = MeasurementModel(
            id=str(uuid4()),
            created_by=current_user.id,
            **input_data.model_dump(),
        )

        return self._repository.add(measurement)

    def update(
        self,
        measurement_id: str,
        input_data: MeasurementUpdate,
        current_user: AuthenticatedUser,
    ) -> MeasurementModel:
        """Atualiza uma medição dentro do escopo permitido."""

        self._require_roles(current_user, MEASUREMENT_EDITOR_ROLES)
        measurement = self._find_by_id(measurement_id)
        current_indicator = self._require_indicator(
            measurement.indicator_id
        )
        current_company = self._require_company(
            current_indicator.company_id
        )
        self._require_company_scope(current_user, current_company)

        target_indicator = self._require_indicator(
            input_data.indicator_id
        )
        target_company = self._require_company(
            target_indicator.company_id
        )
        self._require_company_scope(current_user, target_company)
        self._ensure_period_is_available(
            input_data.indicator_id,
            input_data.reference_date,
            ignored_measurement_id=measurement_id,
        )

        for field_name, value in input_data.model_dump().items():
            setattr(measurement, field_name, value)

        return self._repository.update(measurement)

    def delete(
        self,
        measurement_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exclui uma medição operacional dentro do escopo permitido."""

        self._require_roles(current_user, MEASUREMENT_EDITOR_ROLES)
        measurement = self._find_by_id(measurement_id)
        indicator = self._require_indicator(measurement.indicator_id)
        company = self._require_company(indicator.company_id)
        self._require_company_scope(current_user, company)

        self._repository.delete(measurement)

    def _find_by_id(self, measurement_id: str) -> MeasurementModel:
        """Retorna uma medição existente sem aplicar autorização."""

        measurement = self._repository.find_by_id(measurement_id)

        if measurement is None:
            raise MeasurementNotFoundError(measurement_id)

        return measurement

    def _require_indicator(self, indicator_id: str) -> IndicatorModel:
        """Garante que o indicador informado esteja cadastrado."""

        indicator = self._indicator_repository.find_by_id(indicator_id)

        if indicator is None:
            raise IndicatorNotFoundError(indicator_id)

        return indicator

    def _require_company(self, company_id: str) -> CompanyModel:
        """Garante que a empresa informada esteja cadastrada."""

        company = self._company_repository.find_by_id(company_id)

        if company is None:
            raise CompanyNotFoundError(company_id)

        return company

    def _require_environment(
        self,
        environment_id: str,
    ) -> EnvironmentModel:
        """Garante que o ambiente institucional exista."""

        environment = self._environment_repository.find_by_id(
            environment_id
        )

        if environment is None:
            raise EnvironmentNotFoundError(environment_id)

        return environment

    def _require_tenant(self, tenant_id: str) -> TenantModel:
        """Garante que o tenant institucional exista."""

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        return tenant

    def _require_company_scope(
        self,
        current_user: AuthenticatedUser,
        company: CompanyModel,
    ) -> None:
        """Exige acesso à hierarquia institucional da empresa."""

        environment = self._require_environment(
            company.environment_id
        )
        tenant = self._require_tenant(environment.tenant_id)
        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )

    def _require_roles(
        self,
        current_user: AuthenticatedUser,
        allowed_roles: frozenset[UserRole],
    ) -> None:
        """Exige um papel permitido para a operação."""

        self._authorization_service.require_roles(
            current_user,
            allowed_roles,
        )

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