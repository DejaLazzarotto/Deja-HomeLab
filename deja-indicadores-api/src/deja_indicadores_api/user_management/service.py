from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.core.security import PasswordService
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
from deja_indicadores_api.user_management.repository import UserRepository
from deja_indicadores_api.user_management.schemas import (
    UserCreate,
    UserPasswordSet,
    UserUpdate,
)

USER_ADMINISTRATOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
    }
)


class UserService:
    """Regras de aplicação para usuários institucionais."""

    def __init__(
        self,
        user_repository: UserRepository,
        organization_repository: OrganizationRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        password_service: PasswordService,
        authorization_service: AuthorizationService,
    ) -> None:
        self._user_repository = user_repository
        self._organization_repository = organization_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._password_service = password_service
        self._authorization_service = authorization_service

    def list(
        self,
        current_user: AuthenticatedUser,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        status: UserStatus | None = None,
    ) -> list[UserModel]:
        """Lista usuários dentro do escopo do administrador."""

        self._require_user_administrator(current_user)

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

        return self._user_repository.list(
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
            status=status,
        )

    def find_by_id(
        self,
        user_id: str,
        current_user: AuthenticatedUser,
    ) -> UserModel:
        """Retorna um usuário permitido pelo escopo do administrador."""

        self._require_user_administrator(current_user)
        user = self._find_by_id(user_id)
        self._require_user_scope(current_user, user)

        return user

    def create(
        self,
        input_data: UserCreate,
        current_user: AuthenticatedUser,
    ) -> UserModel:
        """Cadastra um usuário dentro do escopo do administrador."""

        self._require_user_administrator(current_user)
        self._require_input_scope(current_user, input_data)
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
        current_user: AuthenticatedUser,
    ) -> UserModel:
        """Atualiza um usuário dentro do escopo do administrador."""

        self._require_user_administrator(current_user)
        user = self._find_by_id(user_id)
        self._require_user_scope(current_user, user)
        self._require_input_scope(current_user, input_data)
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

    def set_password(
        self,
        user_id: str,
        input_data: UserPasswordSet,
        current_user: AuthenticatedUser,
    ) -> UserModel:
        """Define a senha de um usuário permitido pelo escopo."""

        self._require_user_administrator(current_user)
        user = self._find_by_id(user_id)
        self._require_user_scope(current_user, user)
        user.password_hash = self._password_service.hash(
            input_data.password
        )

        return self._user_repository.update(user)

    def _find_by_id(self, user_id: str) -> UserModel:
        """Retorna um usuário existente sem aplicar autorização."""

        user = self._user_repository.find_by_id(user_id)

        if user is None:
            raise UserNotFoundError(user_id)

        return user

    def _require_user_administrator(
        self,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exige papel autorizado para administrar usuários."""

        self._authorization_service.require_roles(
            current_user,
            USER_ADMINISTRATOR_ROLES,
        )

    def _require_user_scope(
        self,
        current_user: AuthenticatedUser,
        user: UserModel,
    ) -> None:
        """Exige que o usuário-alvo pertença ao escopo permitido."""

        self._authorization_service.require_scope(
            current_user,
            organization_id=user.organization_id,
            tenant_id=user.tenant_id,
            environment_id=user.environment_id,
        )

    def _require_input_scope(
        self,
        current_user: AuthenticatedUser,
        input_data: UserCreate | UserUpdate,
    ) -> None:
        """Exige que o payload permaneça no escopo permitido."""

        self._authorization_service.require_scope(
            current_user,
            organization_id=input_data.organization_id,
            tenant_id=input_data.tenant_id,
            environment_id=input_data.environment_id,
        )

    def _validate_institutional_scope(
        self,
        input_data: UserCreate | UserUpdate,
    ) -> None:
        """Valida a consistência entre vínculos e papel do usuário."""

        if input_data.role == UserRole.PLATFORM_ADMIN:
            if (
                input_data.organization_id is not None
                or input_data.tenant_id is not None
                or input_data.environment_id is not None
            ):
                raise RoleScopeMismatchError(
                    input_data.role.value,
                    "não permite organização, tenant nem ambiente",
                )
            return

        if input_data.organization_id is None:
            raise RoleScopeMismatchError(
                input_data.role.value,
                "exige organização",
            )

        organization = self._require_organization(
            input_data.organization_id
        )
        tenant = self._resolve_tenant(
            input_data.tenant_id,
            organization,
        )
        environment = self._resolve_environment(
            input_data.environment_id,
            tenant,
        )

        self._validate_role_scope(
            input_data.role,
            tenant,
            environment,
        )

    def _require_organization(
        self,
        organization_id: str,
    ) -> OrganizationModel:
        """Exige a existência da organização informada."""

        organization = self._organization_repository.find_by_id(
            organization_id
        )

        if organization is None:
            raise OrganizationNotFoundError(organization_id)

        return organization

    def _resolve_tenant(
        self,
        tenant_id: str | None,
        organization: OrganizationModel,
    ) -> TenantModel | None:
        """Valida e retorna o tenant opcional do usuário."""

        if tenant_id is None:
            return None

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        if tenant.organization_id != organization.id:
            raise TenantDoesNotBelongToOrganizationError(
                tenant.id,
                organization.id,
            )

        return tenant

    def _resolve_environment(
        self,
        environment_id: str | None,
        tenant: TenantModel | None,
    ) -> EnvironmentModel | None:
        """Valida e retorna o ambiente opcional do usuário."""

        if environment_id is None:
            return None

        if tenant is None:
            raise EnvironmentRequiresTenantError(environment_id)

        environment = self._environment_repository.find_by_id(
            environment_id
        )

        if environment is None:
            raise EnvironmentNotFoundError(environment_id)

        if environment.tenant_id != tenant.id:
            raise EnvironmentDoesNotBelongToTenantError(
                environment.id,
                tenant.id,
            )

        return environment

    def _validate_role_scope(
        self,
        role: UserRole,
        tenant: TenantModel | None,
        environment: EnvironmentModel | None,
    ) -> None:
        """Valida os vínculos obrigatórios e proibidos para cada papel."""

        if role == UserRole.ORGANIZATION_ADMIN:
            if tenant is not None or environment is not None:
                raise RoleScopeMismatchError(
                    role.value,
                    "não permite tenant nem ambiente",
                )
            return

        if role == UserRole.TENANT_ADMIN:
            if tenant is None or environment is not None:
                raise RoleScopeMismatchError(
                    role.value,
                    "exige tenant e não permite ambiente",
                )
            return

        if tenant is None or environment is None:
            raise RoleScopeMismatchError(
                role.value,
                "exige tenant e ambiente",
            )