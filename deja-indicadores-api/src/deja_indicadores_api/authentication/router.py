from fastapi import APIRouter

from deja_indicadores_api.authentication.dependencies import (
    AuthenticationServiceDependency,
    CurrentUser,
)
from deja_indicadores_api.authentication.schemas import (
    AccessTokenResponse,
    AuthenticatedUser,
    LoginRequest,
)

router = APIRouter(
    prefix="/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=AccessTokenResponse,
)
def login(
    input_data: LoginRequest,
    service: AuthenticationServiceDependency,
) -> AccessTokenResponse:
    """Autentica um usuário e emite um token JWT de acesso."""

    return service.login(input_data)


@router.get(
    "/me",
    response_model=AuthenticatedUser,
)
def get_authenticated_user(
    current_user: CurrentUser,
) -> AuthenticatedUser:
    """Retorna a identidade e o escopo do usuário autenticado."""

    return current_user