from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from deja_indicadores_api.authentication.exceptions import (
    InactiveUserError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
)
from deja_indicadores_api.authentication.schemas import (
    AccessTokenClaims,
    AccessTokenResponse,
    AuthenticatedUser,
    LoginRequest,
)
from deja_indicadores_api.core.security import (
    AccessTokenService,
    PasswordService,
)
from deja_indicadores_api.user_management.models import UserStatus
from deja_indicadores_api.user_management.repository import UserRepository


class AuthenticationService:
    """Autentica usuários e valida identidades por token."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        access_token_service: AccessTokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._access_token_service = access_token_service

    def login(self, input_data: LoginRequest) -> AccessTokenResponse:
        """Valida as credenciais e emite um token JWT."""

        user = self._user_repository.find_by_organization_and_email(
            input_data.organization_id,
            str(input_data.email),
        )

        if (
            user is None
            or user.password_hash is None
            or not self._password_service.verify(
                input_data.password,
                user.password_hash,
            )
        ):
            raise InvalidCredentialsError

        if user.status != UserStatus.ACTIVE:
            raise InactiveUserError

        access_token = self._access_token_service.create(
            subject=user.id,
            organization_id=user.organization_id,
            tenant_id=user.tenant_id,
            environment_id=user.environment_id,
            role=user.role.value,
        )

        return AccessTokenResponse(
            access_token=access_token,
            expires_in=self._access_token_service.expires_in_seconds,
        )

    def authenticate(self, token: str) -> AuthenticatedUser:
        """Valida o token e retorna a identidade persistida do usuário."""

        try:
            payload = self._access_token_service.decode(token)
            claims = AccessTokenClaims.model_validate(payload)
        except (InvalidTokenError, ValidationError):
            raise InvalidAccessTokenError from None

        user = self._user_repository.find_by_id(claims.sub)

        if user is None or user.status != UserStatus.ACTIVE:
            raise InvalidAccessTokenError

        if (
            user.organization_id != claims.organization_id
            or user.tenant_id != claims.tenant_id
            or user.environment_id != claims.environment_id
            or user.role != claims.role
        ):
            raise InvalidAccessTokenError

        return AuthenticatedUser(
            id=user.id,
            organization_id=user.organization_id,
            tenant_id=user.tenant_id,
            environment_id=user.environment_id,
            name=user.name,
            email=user.email,
            role=user.role,
        )