from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.module_management.exceptions import (
    ModuleNotEnabledError,
    UnknownModuleKeysError,
)
from deja_indicadores_api.module_management.models import ModuleModel
from deja_indicadores_api.module_management.repository import (
    ModuleRepository,
    OrganizationModuleRepository,
)
from deja_indicadores_api.module_management.schemas import (
    OrganizationModuleResponse,
    OrganizationModulesResponse,
    OrganizationModulesUpdate,
)
from deja_indicadores_api.tenant_management.exceptions import (
    OrganizationNotFoundError,
)
from deja_indicadores_api.tenant_management.repository import (
    OrganizationRepository,
)
from deja_indicadores_api.user_management.models import UserRole

PLATFORM_ADMIN_ROLE = frozenset({UserRole.PLATFORM_ADMIN})


class ModuleManagementService:
    """Regras do catálogo e das liberações de módulos."""

    def __init__(
        self,
        module_repository: ModuleRepository,
        organization_module_repository: OrganizationModuleRepository,
        organization_repository: OrganizationRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._module_repository = module_repository
        self._organization_module_repository = (
            organization_module_repository
        )
        self._organization_repository = organization_repository
        self._authorization_service = authorization_service

    def list_catalog(
        self,
        current_user: AuthenticatedUser,
    ) -> list[ModuleModel]:
        """Lista o catálogo para a administração da plataforma."""

        self._require_platform_administrator(current_user)
        return self._module_repository.list()

    def get_organization_modules(
        self,
        organization_id: str,
        current_user: AuthenticatedUser,
    ) -> OrganizationModulesResponse:
        """Retorna o catálogo com os estados de uma organização."""

        self._require_platform_administrator(current_user)
        self._require_organization(organization_id)

        return self._build_organization_response(organization_id)

    def update_organization_modules(
        self,
        organization_id: str,
        input_data: OrganizationModulesUpdate,
        current_user: AuthenticatedUser,
    ) -> OrganizationModulesResponse:
        """Substitui a seleção de módulos em uma única transação."""

        self._require_platform_administrator(current_user)
        self._require_organization(organization_id)

        catalog = self._module_repository.list()
        catalog_keys = [module.key for module in catalog]
        unknown_keys = (
            set(input_data.enabled_modules)
            - set(catalog_keys)
        )

        if unknown_keys:
            raise UnknownModuleKeysError(unknown_keys)

        self._organization_module_repository.replace(
            organization_id=organization_id,
            catalog_keys=catalog_keys,
            enabled_keys=input_data.enabled_modules,
        )

        return self._build_organization_response(organization_id)

    def list_enabled_module_keys(
        self,
        organization_id: str | None,
    ) -> list[str]:
        """Lista as chaves liberadas para uma sessão organizacional."""

        if organization_id is None:
            return []

        return (
            self._organization_module_repository
            .list_enabled_module_keys(organization_id)
        )

    def require_module(
        self,
        current_user: AuthenticatedUser,
        module_key: str,
    ) -> None:
        """Exige que o módulo esteja liberado para o usuário atual."""

        if current_user.role == UserRole.PLATFORM_ADMIN:
            return

        organization_id = current_user.organization_id

        if organization_id is None:
            raise ModuleNotEnabledError(module_key)

        if not self._organization_module_repository.is_enabled(
            organization_id,
            module_key,
        ):
            raise ModuleNotEnabledError(module_key)

    def _build_organization_response(
        self,
        organization_id: str,
    ) -> OrganizationModulesResponse:
        """Monta o catálogo com o estado efetivo da organização."""

        modules = [
            OrganizationModuleResponse(
                key=module.key,
                name=module.name,
                description=module.description,
                display_order=module.display_order,
                enabled=enabled,
            )
            for module, enabled in (
                self._organization_module_repository
                .list_for_organization(organization_id)
            )
        ]

        return OrganizationModulesResponse(
            organization_id=organization_id,
            modules=modules,
        )

    def _require_platform_administrator(
        self,
        current_user: AuthenticatedUser,
    ) -> None:
        """Restringe a operação ao administrador da plataforma."""

        self._authorization_service.require_roles(
            current_user,
            PLATFORM_ADMIN_ROLE,
        )

    def _require_organization(
        self,
        organization_id: str,
    ) -> None:
        """Garante que a organização solicitada exista."""

        organization = self._organization_repository.find_by_id(
            organization_id
        )

        if organization is None:
            raise OrganizationNotFoundError(organization_id)