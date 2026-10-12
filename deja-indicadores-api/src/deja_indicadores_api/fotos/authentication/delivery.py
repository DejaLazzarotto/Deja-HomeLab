"""Preparacao de mensagens de verificacao do Fotos PWA."""

from html import escape

from sqlalchemy.orm import Session

from deja_indicadores_api.core.email import EmailDeliveryError, EmailService
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.repository import (
    FotosVerificationCodeRepository,
)


def build_verification_html(
    *,
    purpose: FotosVerificationPurpose,
    code: str,
) -> str:
    """Prepara a identidade visual HTML dos codigos de verificacao."""

    if purpose == FotosVerificationPurpose.ACTIVATION:
        title = "Ativação da sua conta"
        introduction = "Recebemos uma solicitação para criar sua senha de acesso ao Fotos."
        instruction = "Informe este código no aplicativo para continuar."
    elif purpose == FotosVerificationPurpose.PASSWORD_RESET:
        title = "Recuperação de senha"
        introduction = "Recebemos uma solicitação para redefinir a senha do seu acesso ao Fotos."
        instruction = "Informe este código no aplicativo para criar uma nova senha."
    else:
        raise ValueError("Finalidade de verificacao invalida.")

    safe_code = escape(code)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background-color:#f1f5f9;
font-family:Arial,Helvetica,sans-serif;color:#172033;">
  <table role="presentation" cellpadding="0" cellspacing="0"
    border="0" width="100%"
    style="background-color:#f1f5f9;">
    <tr>
      <td align="center" style="padding:24px 12px;">
        <table role="presentation" cellpadding="0" cellspacing="0"
          border="0" width="100%"
          style="max-width:560px;background-color:#ffffff;
          border-radius:12px;overflow:hidden;">
          <tr>
            <td style="padding:28px 30px;
              background-color:#101d33;color:#ffffff;">
              <div style="font-size:30px;font-weight:bold;
                letter-spacing:-1px;">Fotos</div>
              <div style="font-size:11px;letter-spacing:3px;
                color:#b7c9e6;margin-top:5px;">
                DEJA PLATFORM
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:32px 30px;">
              <h1 style="font-size:25px;line-height:1.3;
                margin:0 0 18px;color:#101827;">
                {title}
              </h1>
              <p style="font-size:15px;line-height:1.7;
                color:#526078;margin:0 0 24px;">
                {introduction}
              </p>
              <table role="presentation" width="100%"
                cellpadding="0" cellspacing="0" border="0"
                style="background-color:#edf4ff;
                border:1px solid #d7e5fa;border-radius:10px;">
                <tr>
                  <td align="center" style="padding:24px 12px;">
                    <div style="font-size:11px;font-weight:bold;
                      letter-spacing:1.5px;color:#2861b5;
                      margin-bottom:14px;">
                      SEU CÓDIGO DE VERIFICAÇÃO
                    </div>
                    <div style="display:inline-block;
                      background-color:#152c4f;color:#ffffff;
                      border-radius:8px;padding:14px 22px;
                      font-size:32px;font-weight:bold;
                      letter-spacing:6px;">
                      {safe_code}
                    </div>
                    <div style="font-size:13px;color:#526b90;
                      margin-top:15px;">
                      Válido por 10 minutos
                    </div>
                  </td>
                </tr>
              </table>
              <p style="font-size:15px;line-height:1.7;
                color:#526078;margin:24px 0 0;">
                {instruction}<br>
                Ele pode ser utilizado apenas uma vez.
              </p>
              <div style="border-top:1px solid #e2e8f0;
                margin:28px 0 18px;"></div>
              <p style="font-size:12px;line-height:1.6;
                color:#718096;margin:0 0 15px;">
                Se você não solicitou este código,
                ignore esta mensagem.
              </p>
              <p style="font-size:13px;font-weight:bold;
                color:#172033;margin:0;">
                Deja Platform &middot; Fotos
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


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
                html_body=build_verification_html(
                    purpose=purpose,
                    code=code,
                ),
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
