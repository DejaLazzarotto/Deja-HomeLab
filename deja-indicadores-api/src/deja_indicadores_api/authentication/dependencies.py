from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.service import AuthenticationService
from deja_indicadores_api.core.config import Settings, get_settings
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.core.security import (
    AccessTokenService,
    PasswordService,
)
from deja_indicadores_api.user_management.repository import UserRepository

DatabaseSession = Annotated[Session, Depends(get_db_session)]
ApplicationSettings = Annotated[Settings, Depends(get_settings)]


def get_authentication_service(
    session: DatabaseSession,
    settings: ApplicationSettings,
) -> AuthenticationService:
    """Cria o serviço de autenticação para a requisição."""

    user_repository = UserRepository(session)
    password_service = PasswordService()
    access_token_service = AccessTokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.access_token_expire_minutes,
    )

    return AuthenticationService(
        user_repository,
        password_service,
        access_token_service,
    )


AuthenticationServiceDependency = Annotated[
    AuthenticationService,
    Depends(get_authentication_service),
]