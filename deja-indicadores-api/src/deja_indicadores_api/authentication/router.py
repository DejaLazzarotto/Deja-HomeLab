from fastapi import APIRouter

from deja_indicadores_api.authentication.dependencies import (
    AuthenticationServiceDependency,
)
from deja_indicadores_api.authentication.schemas import (
    AccessTokenResponse,
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