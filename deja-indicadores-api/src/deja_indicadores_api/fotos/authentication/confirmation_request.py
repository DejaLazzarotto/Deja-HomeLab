"""Coordenacao da confirmacao publica de codigos do Fotos PWA."""

from sqlalchemy.orm import Session

from deja_indicadores_api.core.security import PasswordService
from deja_indicadores_api.fotos.authentication.confirmation import (
    FotosVerificationConfirmationService,
    FotosVerificationInvalidCodeError,
)
from deja_indicadores_api.fotos.authentication.identity import (
    FotosVerificationIdentityService,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.rate_limit_service import FotosAuthRateLimitService
from deja_indicadores_api.fotos.authentication.service import (
    FotosVerificationCodeService,
)


class FotosVerificationConfirmationRequestService:
    """Confirma codigos sem expor identificadores internos de usuarios."""

    def __init__(
        self,
        session: Session,
        code_service: FotosVerificationCodeService,
        password_service: PasswordService,
        rate_limit_service: FotosAuthRateLimitService | None = None,
    ) -> None:
        self._rate_limit = rate_limit_service
        self._identity = FotosVerificationIdentityService(session)
        self._confirmation = FotosVerificationConfirmationService(
            session,
            code_service,
            password_service,
        )

    def confirm(
        self,
        *,
        organization_code: str,
        email: str,
        purpose: FotosVerificationPurpose,
        code: str,
        new_password: str,
        client_ip: str | None = None,
    ) -> None:
        """Localiza a conta no escopo correto e confirma seu codigo."""

        if self._rate_limit is not None:
            if client_ip is None:
                raise ValueError("Endereco IP necessario para rate limiting.")

            allowed = self._rate_limit.allow_confirmation(
                client_ip=client_ip,
                organization_code=organization_code,
                email=email,
            )

            if not allowed:
                raise FotosVerificationInvalidCodeError()

        user = self._identity.find_user(
            organization_code=organization_code,
            email=email,
        )

        if user is None:
            raise FotosVerificationInvalidCodeError()

        self._confirmation.confirm(
            user_id=user.id,
            purpose=purpose,
            code=code,
            new_password=new_password,
        )
