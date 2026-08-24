from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.companies.exceptions import CompanyNotFoundError
from deja_indicadores_api.companies.models import CompanyModel
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
from deja_indicadores_api.measurements.exceptions import (
    IndicatorHasMeasurementsError,
)
from deja_indicadores_api.measurements.repository import MeasurementRepository
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

INDICATOR_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)

INDICATOR_EDITOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
    }
)

INDICATOR_MANAGER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
    }
)


class IndicatorService:
    """Regras de aplicação da Gestão de Indicadores."""

    def __init__(
        self,
        repository: IndicatorRepository,
        company_repository: CompanyRepository,
        measurement_repository: MeasurementRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._company_repository = company_repository
        self._measurement_repository = measurement_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._authorization_service = authorization_service

    def list(
        self,
        current_user: AuthenticatedUser,
        *,
        company_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> list[IndicatorModel]:
        """Lista indicadores dentro do escopo permitido."""

        self._require_roles(current_user, INDICATOR_READER_ROLES)

        if company_id is not None:
            company = self._require_company(company_id)
            self._require_company_scope(current_user, company)

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
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
        )

    def find_by_id(
        self,
        indicator_id: str,
        current_user: AuthenticatedUser,
    ) -> IndicatorModel:
        """Retorna um indicador dentro do escopo permitido."""

        self._require_roles(current_user, INDICATOR_READER_ROLES)
        indicator = self._find_by_id(indicator_id)
        company = self._require_company(indicator.company_id)
        self._require_company_scope(current_user, company)

        return indicator

    def create(
        self,
        input_data: IndicatorCreate,
        current_user: AuthenticatedUser,
    ) -> IndicatorModel:
        """Cadastra um indicador dentro do escopo permitido."""

        self._require_roles(current_user, INDICATOR_EDITOR_ROLES)
        company = self._require_company(input_data.company_id)
        self._require_company_scope(current_user, company)
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
        current_user: AuthenticatedUser,
    ) -> IndicatorModel:
        """Atualiza um indicador dentro do escopo permitido."""

        self._require_roles(current_user, INDICATOR_EDITOR_ROLES)
        indicator = self._find_by_id(indicator_id)
        current_company = self._require_company(indicator.company_id)
        self._require_company_scope(current_user, current_company)
        target_company = self._require_company(input_data.company_id)
        self._require_company_scope(current_user, target_company)
        self._ensure_name_is_available(
            input_data.company_id,
            input_data.name,
            ignored_indicator_id=indicator_id,
        )

        for field_name, value in input_data.model_dump().items():
            setattr(indicator, field_name, value)

        return self._repository.update(indicator)

    def delete(
        self,
        indicator_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exclui um indicador autorizado sem medições cadastradas."""

        self._require_roles(current_user, INDICATOR_MANAGER_ROLES)
        indicator = self._find_by_id(indicator_id)
        company = self._require_company(indicator.company_id)
        self._require_company_scope(current_user, company)

        if self._measurement_repository.exists_for_indicator(indicator_id):
            raise IndicatorHasMeasurementsError(indicator_id)

        self._repository.delete(indicator)

    def _find_by_id(self, indicator_id: str) -> IndicatorModel:
        """Retorna um indicador existente sem aplicar autorização."""

        indicator = self._repository.find_by_id(indicator_id)

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
        """Exige papel permitido e módulo de Indicadores liberado."""

        self._authorization_service.require_roles(
            current_user,
            allowed_roles,
        )
        self._authorization_service.require_module(
            current_user,
            "indicators",
        )

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