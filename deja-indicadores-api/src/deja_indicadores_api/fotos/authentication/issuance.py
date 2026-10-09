"""Emissao transacional de codigos de verificacao do Fotos PWA."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.authentication.eligibility import (
    FotosVerificationEligibility,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationCodeModel,
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


class FotosVerificationIssuanceError(Exception):
    """Erro interno na solicitacao de um codigo."""


class FotosVerificationNotEligibleError(FotosVerificationIssuanceError):
    """Usuario nao habilitado para esta finalidade."""


class FotosVerificationCooldownError(FotosVerificationIssuanceError):
    """Intervalo minimo entre solicitacoes nao cumprido."""


@dataclass(frozen=True, slots=True)
class IssuedFotosVerification:
    """Dados internos para entrega do codigo por e-mail."""

    verification_id: str
    code: str
    expires_at: datetime


class FotosVerificationIssuanceService:
    """Emite codigos dentro de uma transacao de banco."""

    def __init__(
        self,
        session: Session,
        code_service: FotosVerificationCodeService,
    ) -> None:
        self._session = session
        self._code_service = code_service

        self._repository = FotosVerificationCodeRepository(
            session,
        )

        self._eligibility = FotosVerificationEligibility(
            UserModuleAccessRepository(session),
            OrganizationModuleRepository(session),
            OrganizationRepository(session),
        )

    def issue(
        self,
        *,
        user_id: str,
        purpose: FotosVerificationPurpose,
    ) -> IssuedFotosVerification:
        """Emite um codigo e confirma a transacao."""

        try:
            return self._issue_and_commit(
                user_id=user_id,
                purpose=purpose,
            )
        except Exception:
            self._session.rollback()
            raise

    def _issue_and_commit(
        self,
        *,
        user_id: str,
        purpose: FotosVerificationPurpose,
    ) -> IssuedFotosVerification:
        """Executa a emissao com bloqueio do usuario."""

        if purpose not in (
            FotosVerificationPurpose.ACTIVATION,
            FotosVerificationPurpose.PASSWORD_RESET,
        ):
            raise FotosVerificationNotEligibleError()

        user = self._repository.lock_user(user_id)

        if user is None:
            raise FotosVerificationNotEligibleError()

        if not self._eligibility.can_request(
            user=user,
            purpose=purpose,
        ):
            raise FotosVerificationNotEligibleError()

        now = self._code_service.utc_now()

        latest = self._repository.find_latest(
            user_id,
            purpose.value,
            for_update=True,
        )

        if (
            latest is not None
            and latest.delivery_status != "failed"
            and not self._code_service.can_resend(
                created_at=latest.created_at,
                now=now,
            )
        ):
            raise FotosVerificationCooldownError()

        verification_id = self._code_service.generate_verification_id()
        code = self._code_service.generate_code()
        expires_at = self._code_service.expires_at(now)

        code_hash = self._code_service.hash_code(
            verification_id=verification_id,
            user_id=user_id,
            purpose=purpose.value,
            code=code,
        )

        self._repository.invalidate_active(
            user_id,
            purpose.value,
            now,
        )

        verification = FotosVerificationCodeModel(
            id=verification_id,
            user_id=user_id,
            purpose=purpose.value,
            code_hash=code_hash,
            expires_at=expires_at,
            attempts=0,
            consumed_at=None,
            created_at=now,
        )

        self._repository.add(verification)

        self._session.commit()

        return IssuedFotosVerification(
            verification_id=verification_id,
            code=code,
            expires_at=expires_at,
        )
