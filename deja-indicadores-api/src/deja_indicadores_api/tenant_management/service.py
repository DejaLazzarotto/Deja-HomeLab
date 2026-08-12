from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.tenant_management.exceptions import (
    EnvironmentNameAlreadyExistsError,
    EnvironmentNotFoundError,
    OrganizationHasTenantsError,
    OrganizationNameAlreadyExistsError,
    OrganizationNotFoundError,
    TenantHasEnvironmentsError,
    TenantNameAlreadyExistsError,
    TenantNotFoundError,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    OrganizationModel,
    TenantModel,
)
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    OrganizationRepository,
    TenantRepository,
)
from deja_indicadores_api.tenant_management.schemas import (
    EnvironmentCreate,
    EnvironmentUpdate,
    OrganizationCreate,
    OrganizationUpdate,
    TenantCreate,
    TenantUpdate,
)
from deja_indicadores_api.user_management.models import UserRole

INSTITUTIONAL_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
    }
)

PLATFORM_ADMIN_ROLE = frozenset({UserRole.PLATFORM_ADMIN})

ORGANIZATION_EDITOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
    }
)

TENANT_CREATOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
    }
)

TENANT_EDITOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
    }
)

ENVIRONMENT_ADMINISTRATOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
    }
)


class OrganizationService:
    """Regras de aplicação para organizações."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        tenant_repository: TenantRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._organization_repository = organization_repository
        self._tenant_repository = tenant_repository
        self._authorization_service = authorization_service

    def list(
        self,
        current_user: AuthenticatedUser,
        organization_id: str | None = None,
    ) -> list[OrganizationModel]:
        """Lista organizações dentro do escopo permitido."""

        self._require_roles(
            current_user,
            INSTITUTIONAL_READER_ROLES,
        )
        effective_organization_id = (
            self._authorization_service.resolve_organization_list_scope(
                current_user,
                organization_id,
            )
        )

        return self._organization_repository.list(
            organization_id=effective_organization_id,
        )

    def find_by_id(
        self,
        organization_id: str,
        current_user: AuthenticatedUser,
    ) -> OrganizationModel:
        """Retorna uma organização dentro do escopo permitido."""

        self._require_roles(
            current_user,
            INSTITUTIONAL_READER_ROLES,
        )
        organization = self._find_by_id(organization_id)
        self._require_organization_scope(
            current_user,
            organization.id,
        )

        return organization

    def create(
        self,
        input_data: OrganizationCreate,
        current_user: AuthenticatedUser,
    ) -> OrganizationModel:
        """Cadastra uma organização por administração global."""

        self._require_roles(current_user, PLATFORM_ADMIN_ROLE)

        existing_organization = (
            self._organization_repository.find_by_name(input_data.name)
        )

        if existing_organization is not None:
            raise OrganizationNameAlreadyExistsError(input_data.name)

        organization = OrganizationModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._organization_repository.add(organization)

    def update(
        self,
        organization_id: str,
        input_data: OrganizationUpdate,
        current_user: AuthenticatedUser,
    ) -> OrganizationModel:
        """Atualiza uma organização dentro do escopo permitido."""

        self._require_roles(
            current_user,
            ORGANIZATION_EDITOR_ROLES,
        )
        organization = self._find_by_id(organization_id)
        self._require_organization_scope(
            current_user,
            organization.id,
        )
        name_owner = self._organization_repository.find_by_name(
            input_data.name
        )

        if (
            name_owner is not None
            and name_owner.id != organization_id
        ):
            raise OrganizationNameAlreadyExistsError(input_data.name)

        for field_name, value in input_data.model_dump().items():
            setattr(organization, field_name, value)

        return self._organization_repository.update(organization)

    def delete(
        self,
        organization_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exclui uma organização por administração global."""

        self._require_roles(current_user, PLATFORM_ADMIN_ROLE)
        organization = self._find_by_id(organization_id)

        if self._tenant_repository.exists_for_organization(
            organization_id
        ):
            raise OrganizationHasTenantsError(organization_id)

        self._organization_repository.delete(organization)

    def _find_by_id(
        self,
        organization_id: str,
    ) -> OrganizationModel:
        """Retorna uma organização existente sem aplicar autorização."""

        organization = self._organization_repository.find_by_id(
            organization_id
        )

        if organization is None:
            raise OrganizationNotFoundError(organization_id)

        return organization

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

    def _require_organization_scope(
        self,
        current_user: AuthenticatedUser,
        organization_id: str,
    ) -> None:
        """Exige acesso à organização informada."""

        self._authorization_service.require_organization_scope(
            current_user,
            organization_id,
        )


class TenantService:
    """Regras de aplicação para tenants."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._organization_repository = organization_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._authorization_service = authorization_service

    def list(
        self,
        current_user: AuthenticatedUser,
        organization_id: str | None = None,
        tenant_id: str | None = None,
    ) -> list[TenantModel]:
        """Lista tenants dentro do escopo permitido."""

        self._require_roles(
            current_user,
            INSTITUTIONAL_READER_ROLES,
        )
        (
            effective_organization_id,
            effective_tenant_id,
        ) = self._authorization_service.resolve_tenant_list_scope(
            current_user,
            organization_id=organization_id,
            tenant_id=tenant_id,
        )

        return self._tenant_repository.list(
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
        )

    def find_by_id(
        self,
        tenant_id: str,
        current_user: AuthenticatedUser,
    ) -> TenantModel:
        """Retorna um tenant dentro do escopo permitido."""

        self._require_roles(
            current_user,
            INSTITUTIONAL_READER_ROLES,
        )
        tenant = self._find_by_id(tenant_id)
        self._require_tenant_scope(current_user, tenant)

        return tenant

    def create(
        self,
        input_data: TenantCreate,
        current_user: AuthenticatedUser,
    ) -> TenantModel:
        """Cadastra um tenant dentro do escopo permitido."""

        self._require_roles(current_user, TENANT_CREATOR_ROLES)
        organization = self._require_organization(
            input_data.organization_id
        )
        self._authorization_service.require_organization_scope(
            current_user,
            organization.id,
        )

        existing_tenant = (
            self._tenant_repository.find_by_organization_and_name(
                input_data.organization_id,
                input_data.name,
            )
        )

        if existing_tenant is not None:
            raise TenantNameAlreadyExistsError(
                input_data.organization_id,
                input_data.name,
            )

        tenant = TenantModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._tenant_repository.add(tenant)

    def update(
        self,
        tenant_id: str,
        input_data: TenantUpdate,
        current_user: AuthenticatedUser,
    ) -> TenantModel:
        """Atualiza um tenant dentro do escopo permitido."""

        self._require_roles(current_user, TENANT_EDITOR_ROLES)
        tenant = self._find_by_id(tenant_id)
        self._require_tenant_scope(current_user, tenant)
        organization = self._require_organization(
            input_data.organization_id
        )
        self._authorization_service.require_organization_scope(
            current_user,
            organization.id,
        )

        name_owner = (
            self._tenant_repository.find_by_organization_and_name(
                input_data.organization_id,
                input_data.name,
            )
        )

        if name_owner is not None and name_owner.id != tenant_id:
            raise TenantNameAlreadyExistsError(
                input_data.organization_id,
                input_data.name,
            )

        for field_name, value in input_data.model_dump().items():
            setattr(tenant, field_name, value)

        return self._tenant_repository.update(tenant)

    def delete(
        self,
        tenant_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exclui um tenant dentro do escopo permitido."""

        self._require_roles(current_user, TENANT_CREATOR_ROLES)
        tenant = self._find_by_id(tenant_id)
        self._require_tenant_scope(current_user, tenant)

        if self._environment_repository.exists_for_tenant(tenant_id):
            raise TenantHasEnvironmentsError(tenant_id)

        self._tenant_repository.delete(tenant)

    def _find_by_id(self, tenant_id: str) -> TenantModel:
        """Retorna um tenant existente sem aplicar autorização."""

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        return tenant

    def _require_organization(
        self,
        organization_id: str,
    ) -> OrganizationModel:
        """Garante que a organização informada exista."""

        organization = self._organization_repository.find_by_id(
            organization_id
        )

        if organization is None:
            raise OrganizationNotFoundError(organization_id)

        return organization

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

    def _require_tenant_scope(
        self,
        current_user: AuthenticatedUser,
        tenant: TenantModel,
    ) -> None:
        """Exige acesso ao tenant informado."""

        self._authorization_service.require_tenant_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
        )


class EnvironmentService:
    """Regras de aplicação para ambientes."""

    def __init__(
        self,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._authorization_service = authorization_service

    def list(
        self,
        current_user: AuthenticatedUser,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> list[EnvironmentModel]:
        """Lista ambientes dentro do escopo permitido."""

        self._require_roles(
            current_user,
            INSTITUTIONAL_READER_ROLES,
        )
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

        return self._environment_repository.list(
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
        )

    def find_by_id(
        self,
        environment_id: str,
        current_user: AuthenticatedUser,
    ) -> EnvironmentModel:
        """Retorna um ambiente dentro do escopo permitido."""

        self._require_roles(
            current_user,
            INSTITUTIONAL_READER_ROLES,
        )
        environment = self._find_by_id(environment_id)
        tenant = self._require_tenant(environment.tenant_id)
        self._require_environment_scope(
            current_user,
            tenant,
            environment,
        )

        return environment

    def create(
        self,
        input_data: EnvironmentCreate,
        current_user: AuthenticatedUser,
    ) -> EnvironmentModel:
        """Cadastra um ambiente dentro do escopo permitido."""

        self._require_roles(
            current_user,
            ENVIRONMENT_ADMINISTRATOR_ROLES,
        )
        tenant = self._require_tenant(input_data.tenant_id)
        self._authorization_service.require_tenant_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
        )

        existing_environment = (
            self._environment_repository.find_by_tenant_and_name(
                input_data.tenant_id,
                input_data.name,
            )
        )

        if existing_environment is not None:
            raise EnvironmentNameAlreadyExistsError(
                input_data.tenant_id,
                input_data.name,
            )

        environment = EnvironmentModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._environment_repository.add(environment)

    def update(
        self,
        environment_id: str,
        input_data: EnvironmentUpdate,
        current_user: AuthenticatedUser,
    ) -> EnvironmentModel:
        """Atualiza um ambiente dentro do escopo permitido."""

        self._require_roles(
            current_user,
            ENVIRONMENT_ADMINISTRATOR_ROLES,
        )
        environment = self._find_by_id(environment_id)
        current_tenant = self._require_tenant(environment.tenant_id)
        self._require_environment_scope(
            current_user,
            current_tenant,
            environment,
        )
        target_tenant = self._require_tenant(input_data.tenant_id)
        self._authorization_service.require_tenant_scope(
            current_user,
            organization_id=target_tenant.organization_id,
            tenant_id=target_tenant.id,
        )

        name_owner = (
            self._environment_repository.find_by_tenant_and_name(
                input_data.tenant_id,
                input_data.name,
            )
        )

        if (
            name_owner is not None
            and name_owner.id != environment_id
        ):
            raise EnvironmentNameAlreadyExistsError(
                input_data.tenant_id,
                input_data.name,
            )

        for field_name, value in input_data.model_dump().items():
            setattr(environment, field_name, value)

        return self._environment_repository.update(environment)

    def delete(
        self,
        environment_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exclui um ambiente dentro do escopo permitido."""

        self._require_roles(
            current_user,
            ENVIRONMENT_ADMINISTRATOR_ROLES,
        )
        environment = self._find_by_id(environment_id)
        tenant = self._require_tenant(environment.tenant_id)
        self._require_environment_scope(
            current_user,
            tenant,
            environment,
        )
        self._environment_repository.delete(environment)

    def _find_by_id(
        self,
        environment_id: str,
    ) -> EnvironmentModel:
        """Retorna um ambiente existente sem aplicar autorização."""

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

    def _require_environment_scope(
        self,
        current_user: AuthenticatedUser,
        tenant: TenantModel,
        environment: EnvironmentModel,
    ) -> None:
        """Exige acesso ao ambiente informado."""

        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )