from collections.abc import Collection

from deja_indicadores_api.authentication.exceptions import (
    AuthorizationError,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.module_management.exceptions import (
    ModuleNotEnabledError,
)
from deja_indicadores_api.user_management.models import (
    UserModuleRole,
    UserRole,
)


class AuthorizationService:
    """Aplica regras reutilizáveis de papel, escopo e módulos."""

    def require_roles(
        self,
        current_user: AuthenticatedUser,
        allowed_roles: Collection[UserRole],
    ) -> None:
        """Exige que o usuário possua um dos papéis permitidos."""

        if current_user.role not in allowed_roles:
            raise AuthorizationError

    def require_module(
        self,
        current_user: AuthenticatedUser,
        module_key: str,
    ) -> None:
        """Exige um módulo liberado na sessão organizacional."""

        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        if module_key not in current_user.enabled_modules:
            raise ModuleNotEnabledError(module_key)

    def require_module_roles(
        self,
        current_user: AuthenticatedUser,
        *,
        module_key: str,
        allowed_roles: Collection[UserModuleRole],
    ) -> None:
        """Exige acesso individual ao módulo com papel funcional permitido."""

        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        self.require_module(
            current_user,
            module_key,
        )

        module_access = next(
            (
                access
                for access in current_user.module_access
                if access.module_key == module_key
            ),
            None,
        )

        if (
            module_access is None
            or module_access.role not in allowed_roles
        ):
            raise AuthorizationError

    def require_organization_scope(
        self,
        current_user: AuthenticatedUser,
        organization_id: str,
    ) -> None:
        """Exige acesso à organização informada."""

        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        if organization_id != current_user.organization_id:
            raise AuthorizationError

    def require_tenant_scope(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str,
        tenant_id: str,
    ) -> None:
        """Exige acesso à organização e ao tenant informados."""

        self.require_organization_scope(
            current_user,
            organization_id,
        )

        if (
            current_user.role != UserRole.PLATFORM_ADMIN
            and current_user.tenant_id is not None
            and tenant_id != current_user.tenant_id
        ):
            raise AuthorizationError

    def require_scope(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str | None,
        tenant_id: str | None,
        environment_id: str | None,
    ) -> None:
        """Exige que o recurso pertença ao alcance institucional."""

        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        if (
            current_user.organization_id is None
            or organization_id != current_user.organization_id
        ):
            raise AuthorizationError

        if (
            current_user.tenant_id is not None
            and tenant_id != current_user.tenant_id
        ):
            raise AuthorizationError

        if (
            current_user.environment_id is not None
            and environment_id != current_user.environment_id
        ):
            raise AuthorizationError

    def resolve_organization_list_scope(
        self,
        current_user: AuthenticatedUser,
        organization_id: str | None = None,
    ) -> str | None:
        """Resolve o filtro obrigatório de organizações."""

        if current_user.role == UserRole.PLATFORM_ADMIN:
            return organization_id

        effective_organization_id = (
            organization_id or current_user.organization_id
        )

        if effective_organization_id is None:
            raise AuthorizationError

        self.require_organization_scope(
            current_user,
            effective_organization_id,
        )

        return effective_organization_id

    def resolve_tenant_list_scope(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str | None,
        tenant_id: str | None,
    ) -> tuple[str | None, str | None]:
        """Resolve os filtros obrigatórios de tenants."""

        if current_user.role == UserRole.PLATFORM_ADMIN:
            return organization_id, tenant_id

        effective_organization_id = (
            organization_id or current_user.organization_id
        )
        effective_tenant_id = tenant_id or current_user.tenant_id

        if effective_organization_id is None:
            raise AuthorizationError

        self.require_organization_scope(
            current_user,
            effective_organization_id,
        )

        if (
            effective_tenant_id is not None
            and current_user.tenant_id is not None
        ):
            self.require_tenant_scope(
                current_user,
                organization_id=effective_organization_id,
                tenant_id=effective_tenant_id,
            )

        return effective_organization_id, effective_tenant_id

    def resolve_list_scope(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str | None,
        tenant_id: str | None,
        environment_id: str | None,
    ) -> tuple[str | None, str | None, str | None]:
        """Combina filtros opcionais com o escopo obrigatório do usuário."""

        if current_user.role == UserRole.PLATFORM_ADMIN:
            return organization_id, tenant_id, environment_id

        effective_organization_id = (
            organization_id or current_user.organization_id
        )
        effective_tenant_id = tenant_id or current_user.tenant_id
        effective_environment_id = (
            environment_id or current_user.environment_id
        )

        self.require_scope(
            current_user,
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
        )

        return (
            effective_organization_id,
            effective_tenant_id,
            effective_environment_id,
        )