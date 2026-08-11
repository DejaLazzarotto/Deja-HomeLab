from uuid import uuid4

from deja_indicadores_api.tenant_management.exceptions import (
    EnvironmentNotFoundError,
    OrganizationNotFoundError,
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
from deja_indicadores_api.user_management.exceptions import (
    EnvironmentDoesNotBelongToTenantError,
    EnvironmentRequiresTenantError,
    RoleScopeMismatchError,
    TenantDoesNotBelongToOrganizationError,
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from deja_indicadores_api.user_management.models import (
    UserModel,
    UserRole,
    UserStatus,
)
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)
from deja_indicadores_api.user_management.schemas import (
    UserCreate,
    UserUpdate,
)


class UserService:
    """Regras de aplicação para usuários institucionais."""

    def __init__(
        self,
        user_repository: UserRepository,
        organization_repository: OrganizationRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:
        self._user_repository = user_repository
        self._organization_repository = organization_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository

    def list(
        self,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        status: UserStatus | None = None,
    ) -> list[UserModel]:
        """Lista usuários com filtros institucionais opcionais."""

        return self._user_repository.list(
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
            status=status,
        )

    def find_by_id(self, user_id: str) -> UserModel:
        """Retorna um usuário pelo identificador."""

        user = self._user_repository.find_by_id(user_id)

        if user is None:
            raise UserNotFoundError(user_id)

        return user

    def create(self, input_data: UserCreate) -> UserModel:
        """Cadastra um novo usuário institucional."""

        self._validate_institutional_scope(input_data)

        existing_user = (
            self._user_repository.find_by_organization_and_email(
                input_data.organization_id,
                str(input_data.email),
            )
        )

        if existing_user is not None:
            raise UserEmailAlreadyExistsError(
                input_data.organization_id,
                str(input_data.email),
            )

        user = UserModel(
            id=str(uuid4()),
            **input_data.model_dump(),
        )

        return self._user_repository.add(user)

    def update(
        self,
        user_id: str,
        input_data: UserUpdate,
    ) -> UserModel:
        """Atualiza integralmente um usuário existente."""

        user = self.find_by_id(user_id)
        self._validate_institutional_scope(input_data)

        email_owner = (
            self._user_repository.find_by_organization_and_email(
                input_data.organization_id,
                str(input_data.email),
            )
        )

        if email_owner is not None and email_owner.id != user_id:
            raise UserEmailAlreadyExistsError(
                input_data.organization_id,
                str(input_data.email),
            )

        for field_name, value in input_data.model_dump().items():
            setattr(user, field_name, value)

        return self._user_repository.update(user)

    def _validate_institutional_scope(
        self,
        input_data: UserCreate | UserUpdate,
    ) -> None:
        """Valida a consistência entre vínculos e papel do usuário."""

        self._require_organization(input_data.organization_id)

        tenant = self._validate_tenant_scope(
            organization_id=input_data.organization_id,
            tenant_id=input_data.tenant_id,
        )
        self._validate_environment_scope(
            tenant_id=input_data.tenant_id,
            environment_id=input_data.environment_id,
        )
        self._validate_role_scope(
            role=input_data.role,
            tenant=tenant,
            environment_id=input_data.environment_id,
        )

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

    def _validate_tenant_scope(
        self,
        organization_id: str,
        tenant_id: str | None,
    ) -> TenantModel | None:
        """Valida a existência e a organização do tenant opcional."""

        if tenant_id is None:
            return None

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        if tenant.organization_id != organization_id:
            raise TenantDoesNotBelongToOrganizationError(
                tenant_id,
                organization_id,
            )

        return tenant

    def _validate_environment_scope(
        self,
        tenant_id: str | None,
        environment_id: str | None,
    ) -> EnvironmentModel | None:
        """Valida a existência e o tenant do ambiente opcional."""

        if environment_id is None:
            return None

        if tenant_id is None:
            raise EnvironmentRequiresTenantError(environment_id)

        environment = self._environment_repository.find_by_id(
            environment_id
        )

        if environment is None:
            raise EnvironmentNotFoundError(environment_id)

        if environment.tenant_id != tenant_id:
            raise EnvironmentDoesNotBelongToTenantError(
                environment_id,
                tenant_id,
            )

        return environment

    def _validate_role_scope(
        self,
        role: UserRole,
        tenant: TenantModel | None,
        environment_id: str | None,
    ) -> None:
        """Garante que o papel seja compatível com os vínculos."""

        if role == UserRole.ORGANIZATION_ADMIN:
            if tenant is not None or environment_id is not None:
                raise RoleScopeMismatchError(
                    role.value,
                    "o administrador da organização não pode possuir "
                    "tenant ou ambiente",
                )
            return

        if role == UserRole.TENANT_ADMIN:
            if tenant is None:
                raise RoleScopeMismatchError(
                    role.value,
                    "o administrador de tenant exige um tenant",
                )

            if environment_id is not None:
                raise RoleScopeMismatchError(
                    role.value,
                    "o administrador de tenant não pode possuir ambiente",
                )
            return

        if tenant is None:
            raise RoleScopeMismatchError(
                role.value,
                "o papel exige um tenant",
            )