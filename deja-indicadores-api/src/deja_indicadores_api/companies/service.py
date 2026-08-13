from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.companies.exceptions import (
    CompanyDocumentAlreadyExistsError,
    CompanyNotFoundError,
)
from deja_indicadores_api.companies.models import CompanyModel
from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.companies.schemas import CompanyCreate, CompanyUpdate
from deja_indicadores_api.indicators.exceptions import (
    CompanyHasIndicatorsError,
)
from deja_indicadores_api.indicators.repository import IndicatorRepository
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

COMPANY_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)

COMPANY_MANAGER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
    }
)


class CompanyService:
    """Regras de aplicação da Gestão de Empresas."""

    def __init__(
        self,
        repository: CompanyRepository,
        indicator_repository: IndicatorRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._indicator_repository = indicator_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._authorization_service = authorization_service

    def list(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> list[CompanyModel]:
        """Lista empresas dentro do escopo permitido."""

        self._require_roles(current_user, COMPANY_READER_ROLES)
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
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
        )

    def find_by_id(
        self,
        company_id: str,
        current_user: AuthenticatedUser,
    ) -> CompanyModel:
        """Retorna uma empresa dentro do escopo permitido."""

        self._require_roles(current_user, COMPANY_READER_ROLES)
        company = self._find_by_id(company_id)
        environment, tenant = self._resolve_company_scope(company)
        self._require_company_scope(
            current_user,
            environment,
            tenant,
        )

        return company

    def create(
        self,
        input_data: CompanyCreate,
        current_user: AuthenticatedUser,
    ) -> CompanyModel:
        """Cadastra uma empresa dentro do escopo permitido."""

        self._require_roles(current_user, COMPANY_MANAGER_ROLES)
        environment = self._require_environment(
            input_data.environment_id
        )
        tenant = self._require_tenant(environment.tenant_id)
        self._require_company_scope(
            current_user,
            environment,
            tenant,
        )
        existing_company = self._repository.find_by_document(
            input_data.document
        )

        if existing_company is not None:
            raise CompanyDocumentAlreadyExistsError(input_data.document)

        company = CompanyModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._repository.add(company)

    def update(
        self,
        company_id: str,
        input_data: CompanyUpdate,
        current_user: AuthenticatedUser,
    ) -> CompanyModel:
        """Atualiza integralmente uma empresa dentro do escopo permitido."""

        self._require_roles(current_user, COMPANY_MANAGER_ROLES)
        company = self._find_by_id(company_id)
        current_environment, current_tenant = (
            self._resolve_company_scope(company)
        )
        self._require_company_scope(
            current_user,
            current_environment,
            current_tenant,
        )
        target_environment = self._require_environment(
            input_data.environment_id
        )
        target_tenant = self._require_tenant(
            target_environment.tenant_id
        )
        self._require_company_scope(
            current_user,
            target_environment,
            target_tenant,
        )
        document_owner = self._repository.find_by_document(
            input_data.document
        )

        if document_owner is not None and document_owner.id != company_id:
            raise CompanyDocumentAlreadyExistsError(input_data.document)

        for field_name, value in input_data.model_dump().items():
            setattr(company, field_name, value)

        return self._repository.update(company)

    def delete(
        self,
        company_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exclui uma empresa autorizada sem indicadores cadastrados."""

        self._require_roles(current_user, COMPANY_MANAGER_ROLES)
        company = self._find_by_id(company_id)
        environment, tenant = self._resolve_company_scope(company)
        self._require_company_scope(
            current_user,
            environment,
            tenant,
        )

        if self._indicator_repository.exists_for_company(company_id):
            raise CompanyHasIndicatorsError(company_id)

        self._repository.delete(company)

    def _find_by_id(self, company_id: str) -> CompanyModel:
        """Retorna uma empresa existente sem aplicar autorização."""

        company = self._repository.find_by_id(company_id)

        if company is None:
            raise CompanyNotFoundError(company_id)

        return company

    def _require_environment(
        self,
        environment_id: str,
    ) -> EnvironmentModel:
        """Garante que o ambiente informado exista."""

        environment = self._environment_repository.find_by_id(
            environment_id
        )

        if environment is None:
            raise EnvironmentNotFoundError(environment_id)

        return environment

    def _require_tenant(self, tenant_id: str) -> TenantModel:
        """Garante que o tenant informado exista."""

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        return tenant

    def _resolve_company_scope(
        self,
        company: CompanyModel,
    ) -> tuple[EnvironmentModel, TenantModel]:
        """Resolve a hierarquia institucional real da empresa."""

        environment = self._require_environment(
            company.environment_id
        )
        tenant = self._require_tenant(environment.tenant_id)

        return environment, tenant

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

    def _require_company_scope(
        self,
        current_user: AuthenticatedUser,
        environment: EnvironmentModel,
        tenant: TenantModel,
    ) -> None:
        """Exige acesso à hierarquia institucional da empresa."""

        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )