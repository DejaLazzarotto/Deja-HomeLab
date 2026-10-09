"""Regras de elegibilidade para verificacao do Fotos PWA."""

from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.module_management.repository import (
    OrganizationModuleRepository,
)
from deja_indicadores_api.tenant_management.models import (
    TenantManagementStatus,
)
from deja_indicadores_api.tenant_management.repository import (
    OrganizationRepository,
)
from deja_indicadores_api.user_management.models import (
    UserModel,
    UserModuleRole,
    UserStatus,
)
from deja_indicadores_api.user_management.repository import (
    UserModuleAccessRepository,
)


class FotosVerificationEligibility:
    """Verifica se um usuario pode solicitar codigo do Fotos."""

    def __init__(
        self,
        module_access_repository: UserModuleAccessRepository,
        organization_module_repository: OrganizationModuleRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        self._module_access_repository = module_access_repository
        self._organization_module_repository = organization_module_repository
        self._organization_repository = organization_repository

    def can_request(
        self,
        *,
        user: UserModel,
        purpose: FotosVerificationPurpose,
    ) -> bool:
        """Valida as condicoes de acesso e a finalidade."""

        if user.status != UserStatus.ACTIVE:
            return False

        if user.organization_id is None:
            return False

        organization = self._organization_repository.find_by_id(user.organization_id)

        if organization is None or organization.status != TenantManagementStatus.ACTIVE:
            return False

        if not self._organization_module_repository.is_enabled(
            user.organization_id,
            "fotos",
        ):
            return False

        access = self._module_access_repository.find(
            user.id,
            "fotos",
        )

        if access is None:
            return False

        if access.role not in (
            UserModuleRole.VIEWER,
            UserModuleRole.MANAGER,
        ):
            return False

        if purpose == FotosVerificationPurpose.ACTIVATION:
            return not bool(user.password_hash)

        if purpose == FotosVerificationPurpose.PASSWORD_RESET:
            return bool(user.password_hash)

        return False
