"""Confirmacao de codigos e definicao de senha do Fotos PWA."""

from sqlalchemy.orm import Session

from deja_indicadores_api.core.security import PasswordService
from deja_indicadores_api.fotos.authentication.eligibility import (
    FotosVerificationEligibility,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.repository import (
    FotosVerificationCodeRepository,
)
from deja_indicadores_api.fotos.authentication.service import (
    FotosVerificationCodeService,
)
from deja_indicadores_api.module_management.repository import (
    OrganizationModuleRepository,
)
from deja_indicadores_api.tenant_management.repository import (
    OrganizationRepository,
)
from deja_indicadores_api.user_management.repository import (
    UserModuleAccessRepository,
)


class FotosVerificationConfirmationError(Exception):
    """Falha na confirmacao de um codigo."""


class FotosVerificationInvalidCodeError(FotosVerificationConfirmationError):
    """Codigo incorreto, expirado, consumido ou indisponivel."""


class FotosVerificationInvalidPasswordError(FotosVerificationConfirmationError):
    """Senha fora dos limites permitidos."""


class FotosVerificationConfirmationService:
    """Confirma codigos e atualiza senhas de forma transacional."""

    def __init__(
        self,
        session: Session,
        code_service: FotosVerificationCodeService,
        password_service: PasswordService,
    ) -> None:
        self._session = session
        self._code_service = code_service
        self._password_service = password_service

        self._repository = FotosVerificationCodeRepository(session)
        self._eligibility = FotosVerificationEligibility(
            UserModuleAccessRepository(session),
            OrganizationModuleRepository(session),
            OrganizationRepository(session),
        )

    def confirm(
        self,
        *,
        user_id: str,
        purpose: FotosVerificationPurpose,
        code: str,
        new_password: str,
    ) -> None:
        """Confirma o codigo e define a nova senha."""

        if not 8 <= len(new_password) <= 128:
            raise FotosVerificationInvalidPasswordError()

        if purpose not in (
            FotosVerificationPurpose.ACTIVATION,
            FotosVerificationPurpose.PASSWORD_RESET,
        ):
            raise FotosVerificationInvalidCodeError()

        try:
            self._confirm_and_commit(
                user_id=user_id,
                purpose=purpose,
                code=code,
                new_password=new_password,
            )
        except Exception:
            self._session.rollback()
            raise

    def _confirm_and_commit(
        self,
        *,
        user_id: str,
        purpose: FotosVerificationPurpose,
        code: str,
        new_password: str,
    ) -> None:
        """Executa a confirmacao sob bloqueio transacional."""

        user = self._repository.lock_user(user_id)

        if user is None or not self._eligibility.can_request(
            user=user,
            purpose=purpose,
        ):
            raise FotosVerificationInvalidCodeError()

        verification = self._repository.find_latest(
            user_id,
            purpose.value,
            for_update=True,
        )

        now = self._code_service.utc_now()

        if (
            verification is None
            or verification.delivery_status != "sent"
            or not self._code_service.is_usable(
                expires_at=verification.expires_at,
                attempts=verification.attempts,
                consumed_at=verification.consumed_at,
                now=now,
            )
        ):
            raise FotosVerificationInvalidCodeError()

        valid = self._code_service.verify_code(
            verification_id=verification.id,
            user_id=user_id,
            purpose=purpose.value,
            code=code,
            expected_hash=verification.code_hash,
        )

        if not valid:
            self._repository.increment_attempts(verification)
            self._session.commit()
            raise FotosVerificationInvalidCodeError()

        user.password_hash = self._password_service.hash(new_password)

        self._repository.consume(verification, now)

        self._session.commit()
