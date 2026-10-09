"""Preparacao de mensagens de verificacao do Fotos PWA."""

from sqlalchemy.orm import Session

from deja_indicadores_api.core.email import EmailDeliveryError, EmailService
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.repository import (
    FotosVerificationCodeRepository,
)


def build_verification_email(
    *,
    purpose: FotosVerificationPurpose,
    code: str,
) -> tuple[str, str]:
    """Prepara assunto e corpo da mensagem de verificacao."""

    if purpose == FotosVerificationPurpose.ACTIVATION:
        subject = "Fotos - Ativacao da sua conta"
        introduction = "Recebemos uma solicitacao para ativar o seu acesso ao Fotos."

    elif purpose == FotosVerificationPurpose.PASSWORD_RESET:
        subject = "Fotos - Recuperacao de senha"
        introduction = "Recebemos uma solicitacao para redefinir a senha do seu acesso ao Fotos."

    else:
        raise ValueError("Finalidade de verificacao invalida.")

    body = (
        f"{introduction}\n\n"
        f"Seu codigo de verificacao e: {code}\n\n"
        "O codigo e valido por 10 minutos e pode ser utilizado "
        "uma unica vez.\n\n"
        "Se voce nao solicitou este codigo, ignore esta mensagem.\n\n"
        "Equipe Deja Fotos"
    )

    return subject, body


class FotosVerificationDeliveryStateError(Exception):
    """Falha ao registrar o estado da entrega."""


class FotosVerificationDeliveryService:
    """Envia codigos e registra o resultado SMTP."""

    def __init__(
        self,
        session: Session,
        email_service: EmailService,
    ) -> None:
        self._session = session
        self._email_service = email_service
        self._repository = FotosVerificationCodeRepository(session)

    def deliver(
        self,
        *,
        verification_id: str,
        recipient: str,
        purpose: FotosVerificationPurpose,
        code: str,
    ) -> None:
        """Envia o codigo e atualiza seu estado de entrega."""

        subject, body = build_verification_email(
            purpose=purpose,
            code=code,
        )

        try:
            self._email_service.send(
                recipient=recipient,
                subject=subject,
                body=body,
            )
        except EmailDeliveryError:
            self._record_status(verification_id, "failed")
            raise

        self._record_status(verification_id, "sent")

    def _record_status(
        self,
        verification_id: str,
        status: str,
    ) -> None:
        """Persiste o resultado da tentativa SMTP."""

        try:
            updated = self._repository.update_delivery_status(
                verification_id,
                status,
            )

            if not updated:
                raise FotosVerificationDeliveryStateError("Estado de entrega indisponivel.")

            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
