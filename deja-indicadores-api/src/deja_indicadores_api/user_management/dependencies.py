from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.core.security import PasswordService
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    OrganizationRepository,
    TenantRepository,
)
from deja_indicadores_api.user_management.repository import UserRepository
from deja_indicadores_api.user_management.service import UserService

DatabaseSession = Annotated[Session, Depends(get_db_session)]


def get_user_service(
    session: DatabaseSession,
) -> UserService:
    """Cria o serviço de usuários para a sessão da requisição."""

    user_repository = UserRepository(session)
    organization_repository = OrganizationRepository(session)
    tenant_repository = TenantRepository(session)
    environment_repository = EnvironmentRepository(session)
    password_service = PasswordService()
    authorization_service = AuthorizationService()

    return UserService(
        user_repository,
        organization_repository,
        tenant_repository,
        environment_repository,
        password_service,
        authorization_service,
    )


UserServiceDependency = Annotated[
    UserService,
    Depends(get_user_service),
]