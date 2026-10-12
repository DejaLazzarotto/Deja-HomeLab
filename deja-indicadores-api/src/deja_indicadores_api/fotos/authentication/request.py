"""Solicitacao de codigos de verificacao para o Fotos PWA."""

from sqlalchemy.orm import Session

from deja_indicadores_api.core.email import EmailDeliveryError, EmailService
from deja_indicadores_api.fotos.authentication.delivery import (
    FotosVerificationDeliveryService,
)
from deja_indicadores_api.fotos.authentication.identity import (
    FotosVerificationIdentityService,
)
from deja_indicadores_api.fotos.authentication.issuance import (
    FotosVerificationCooldownError,
    FotosVerificationIssuanceService,
    FotosVerificationNotEligibleError,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.rate_limit_service import FotosAuthRateLimitService
from deja_indicadores_api.fotos.authentication.service import (
    FotosVerificationCodeService,
)


class FotosVerificationRequestService:
    """Coordena identificacao, emissao e entrega dos codigos."""

    def __init__(
        self,
        session: Session,
        code_service: FotosVerificationCodeService,
        email_service: EmailService,
        rate_limit_service: FotosAuthRateLimitService | None = None,
    ) -> None:
        self._rate_limit = rate_limit_service
        self._identity = FotosVerificationIdentityService(session)
        self._issuance = FotosVerificationIssuanceService(
            session,
            code_service,
        )
        self._delivery = FotosVerificationDeliveryService(
            session,
            email_service,
        )

    def request_code(
        self,
        *,
        organization_code: str,
        email: str,
        purpose: FotosVerificationPurpose,
        client_ip: str | None = None,
    ) -> None:
        """Solicita codigo sem revelar se a conta esta cadastrada."""

        if self._rate_limit is not None:
            if client_ip is None:
                raise ValueError("Endereco IP necessario para rate limiting.")

            allowed = self._rate_limit.allow_request(
                client_ip=client_ip,
                organization_code=organization_code,
                email=email,
            )

            if not allowed:
                return

        user = self._identity.find_user(
            organization_code=organization_code,
            email=email,
        )

        if user is None:
            return

        try:
            issued = self._issuance.issue(
                user_id=user.id,
                purpose=purpose,
            )
        except (
            FotosVerificationNotEligibleError,
            FotosVerificationCooldownError,
        ):
            return

        try:
            self._delivery.deliver(
                verification_id=issued.verification_id,
                recipient=user.email,
                purpose=purpose,
                code=issued.code,
            )
        except EmailDeliveryError:
            return
