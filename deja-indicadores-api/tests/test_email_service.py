"""Testes unitarios do servico SMTP."""

from types import SimpleNamespace
from unittest.mock import patch

from deja_indicadores_api.core.email import EmailService


def test_send_email_uses_ssl_and_authentication():
    settings = SimpleNamespace(
        smtp_host="mail.deja.com.br",
        smtp_port=465,
        smtp_username="teste@deja.com.br",
        smtp_password="senha-de-teste",
        smtp_from_email="teste@deja.com.br",
        smtp_timeout_seconds=15,
    )

    with patch(
        "deja_indicadores_api.core.email.smtplib.SMTP_SSL"
    ) as smtp_class:
        EmailService(settings).send(
            recipient="destino@example.com",
            subject="Teste SMTP",
            body="Mensagem de teste.",
        )

        smtp_class.assert_called_once()
        smtp = smtp_class.return_value.__enter__.return_value

        smtp.login.assert_called_once_with(
            "teste@deja.com.br",
            "senha-de-teste",
        )
        smtp.send_message.assert_called_once()


def test_send_email_rejects_missing_configuration():
    """Impede envio quando a senha SMTP nao foi configurada."""
    import pytest

    from deja_indicadores_api.core.email import EmailDeliveryError

    settings = SimpleNamespace(
        smtp_host="mail.deja.com.br",
        smtp_port=465,
        smtp_username="teste@deja.com.br",
        smtp_password="",
        smtp_from_email="teste@deja.com.br",
        smtp_timeout_seconds=15,
    )

    with patch(
        "deja_indicadores_api.core.email.smtplib.SMTP_SSL"
    ) as smtp_class:
        with pytest.raises(
            EmailDeliveryError,
            match="nao|não",
        ):
            EmailService(settings).send(
                recipient="destino@example.com",
                subject="Teste",
                body="Mensagem de teste.",
            )

        smtp_class.assert_not_called()


def test_send_email_handles_authentication_failure():
    """Trata uma falha de autenticacao sem expor credenciais."""
    import smtplib

    import pytest

    from deja_indicadores_api.core.email import EmailDeliveryError

    settings = SimpleNamespace(
        smtp_host="mail.deja.com.br",
        smtp_port=465,
        smtp_username="teste@deja.com.br",
        smtp_password="senha-de-teste",
        smtp_from_email="teste@deja.com.br",
        smtp_timeout_seconds=15,
    )

    with patch(
        "deja_indicadores_api.core.email.smtplib.SMTP_SSL"
    ) as smtp_class:
        smtp = smtp_class.return_value.__enter__.return_value

        smtp.login.side_effect = smtplib.SMTPAuthenticationError(
            535,
            b"Authentication failed",
        )

        with pytest.raises(EmailDeliveryError) as error:
            EmailService(settings).send(
                recipient="destino@example.com",
                subject="Teste",
                body="Mensagem de teste.",
            )

        assert str(error.value) == (
            "Não foi possível enviar o e-mail."
        )
        assert "senha-de-teste" not in str(error.value)
