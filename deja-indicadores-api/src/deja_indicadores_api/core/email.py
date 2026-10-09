"""Serviço de envio de mensagens por SMTP seguro."""

import smtplib
import ssl
from email.message import EmailMessage

from deja_indicadores_api.core.config import Settings


class EmailDeliveryError(Exception):
    """Falha no envio de uma mensagem de e-mail."""


class EmailService:
    """Envia mensagens usando SMTP com SSL/TLS."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(
        self,
        *,
        recipient: str,
        subject: str,
        body: str,
    ) -> None:
        """Envia uma mensagem de texto simples."""

        settings = self._settings

        if not all(
            (
                settings.smtp_host,
                settings.smtp_username,
                settings.smtp_password,
                settings.smtp_from_email,
            )
        ):
            raise EmailDeliveryError(
                "O serviço SMTP não está configurado."
            )

        message = EmailMessage()
        message["From"] = settings.smtp_from_email
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL(
                host=settings.smtp_host,
                port=settings.smtp_port,
                timeout=settings.smtp_timeout_seconds,
                context=context,
            ) as smtp:
                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password,
                )
                smtp.send_message(message)

        except (smtplib.SMTPException, OSError):
            raise EmailDeliveryError(
                "Não foi possível enviar o e-mail."
            ) from None