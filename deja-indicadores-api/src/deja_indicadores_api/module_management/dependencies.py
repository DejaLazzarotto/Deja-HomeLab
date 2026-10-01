from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.dependencies import CurrentUser
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.module_management.repository import (
    ModuleRepository,
    OrganizationModuleRepository,
)
from deja_indicadores_api.module_management.service import (
    ModuleManagementService,
)
from deja_indicadores_api.tenant_management.repository import (
    OrganizationRepository,
)
from deja_indicadores_api.user_management.models import UserModuleRole

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_module_management_service(
    session: DatabaseSession,
) -> ModuleManagementService:
    """Cria o serviço modular para a sessão da requisição."""

    module_repository = ModuleRepository(session)
    organization_module_repository = OrganizationModuleRepository(
        session
    )
    organization_repository = OrganizationRepository(session)
    authorization_service = AuthorizationService()

    return ModuleManagementService(
        module_repository,
        organization_module_repository,
        organization_repository,
        authorization_service,
    )


ModuleManagementServiceDependency = Annotated[
    ModuleManagementService,
    Depends(get_module_management_service),
]


def require_module(
    module_key: str,
) -> Callable[..., AuthenticatedUser]:
    """Cria uma dependência que exige um módulo comercial liberado."""

    def authorize(
        current_user: CurrentUser,
        service: ModuleManagementServiceDependency,
    ) -> AuthenticatedUser:
        service.require_module(
            current_user,
            module_key,
        )
        return current_user

    return authorize


def require_module_roles(
    module_key: str,
    *allowed_roles: UserModuleRole,
) -> Callable[..., AuthenticatedUser]:
    """Exige acesso individual ao módulo com um papel funcional permitido."""

    authorization_service = AuthorizationService()

    def authorize(
        current_user: CurrentUser,
    ) -> AuthenticatedUser:
        authorization_service.require_module_roles(
            current_user,
            module_key=module_key,
            allowed_roles=allowed_roles,
        )

        return current_user

    return authorize