from collections.abc import Collection

from deja_indicadores_api.authentication.exceptions import (
    AuthorizationError,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.user_management.models import UserRole


class AuthorizationService:
    """Aplica regras reutilizáveis de papel e escopo institucional."""

    def require_roles(
        self,
        current_user: AuthenticatedUser,
        allowed_roles: Collection[UserRole],
    ) -> None:
        """Exige que o usuário possua um dos papéis permitidos."""

        if current_user.role not in allowed_roles:
            raise AuthorizationError

    def require_scope(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str,
        tenant_id: str | None,
        environment_id: str | None,
    ) -> None:
        """Exige que o recurso pertença ao alcance institucional."""

        if organization_id != current_user.organization_id:
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

    def resolve_list_scope(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str | None,
        tenant_id: str | None,
        environment_id: str | None,
    ) -> tuple[str, str | None, str | None]:
        """Combina filtros opcionais com o escopo obrigatório do usuário."""

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