"""Testes das mensagens de verificacao do Fotos PWA."""

import pytest

from deja_indicadores_api.fotos.authentication.delivery import (
    build_verification_email,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)


@pytest.mark.parametrize(
    ("purpose", "expected_subject", "expected_text"),
    [
        (
            FotosVerificationPurpose.ACTIVATION,
            "Fotos - Ativacao da sua conta",
            "ativar o seu acesso",
        ),
        (
            FotosVerificationPurpose.PASSWORD_RESET,
            "Fotos - Recuperacao de senha",
            "redefinir",
        ),
    ],
)
def test_build_verification_email(
    purpose: FotosVerificationPurpose,
    expected_subject: str,
    expected_text: str,
) -> None:
    """Prepara corretamente as duas mensagens de verificacao."""

    subject, body = build_verification_email(
        purpose=purpose,
        code="012345",
    )

    assert subject == expected_subject
    assert expected_text in body
    assert "012345" in body
    assert "10 minutos" in body
    assert "uma unica vez" in body
    assert "ignore esta mensagem" in body


def test_build_verification_email_rejects_invalid_purpose() -> None:
    """Nao aceita finalidades desconhecidas."""

    with pytest.raises(ValueError):
        build_verification_email(
            purpose="invalid",
            code="012345",
        )


def test_delivery_service_records_success() -> None:
    """Registra entrega aceita pelo servidor SMTP."""

    from unittest.mock import Mock

    from deja_indicadores_api.fotos.authentication.delivery import (
        FotosVerificationDeliveryService,
    )

    session = Mock()
    email_service = Mock()

    service = FotosVerificationDeliveryService(
        session,
        email_service,
    )

    service._repository = Mock()
    service._repository.update_delivery_status.return_value = True

    service.deliver(
        verification_id="verificacao-001",
        recipient="usuario@exemplo.com",
        purpose=FotosVerificationPurpose.ACTIVATION,
        code="012345",
    )

    email_service.send.assert_called_once()

    kwargs = email_service.send.call_args.kwargs

    assert kwargs["recipient"] == "usuario@exemplo.com"
    assert kwargs["subject"] == "Fotos - Ativacao da sua conta"
    assert "012345" in kwargs["body"]
    assert "10 minutos" in kwargs["body"]

    service._repository.update_delivery_status.assert_called_once_with(
        "verificacao-001",
        "sent",
    )

    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_delivery_service_records_smtp_failure() -> None:
    """Registra falha SMTP sem realizar reenvio automatico."""

    from unittest.mock import Mock

    from deja_indicadores_api.core.email import EmailDeliveryError
    from deja_indicadores_api.fotos.authentication.delivery import (
        FotosVerificationDeliveryService,
    )

    session = Mock()
    email_service = Mock()
    email_service.send.side_effect = EmailDeliveryError("Falha simulada.")

    service = FotosVerificationDeliveryService(
        session,
        email_service,
    )

    service._repository = Mock()
    service._repository.update_delivery_status.return_value = True

    with pytest.raises(EmailDeliveryError):
        service.deliver(
            verification_id="verificacao-001",
            recipient="usuario@exemplo.com",
            purpose=FotosVerificationPurpose.PASSWORD_RESET,
            code="012345",
        )

    email_service.send.assert_called_once()

    kwargs = email_service.send.call_args.kwargs

    assert kwargs["recipient"] == "usuario@exemplo.com"
    assert kwargs["subject"] == "Fotos - Recuperacao de senha"
    assert "012345" in kwargs["body"]

    service._repository.update_delivery_status.assert_called_once_with(
        "verificacao-001",
        "failed",
    )

    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_delivery_service_rolls_back_when_status_update_fails() -> None:
    """Preserva a transacao quando o registro do envio falha."""

    from unittest.mock import Mock

    from deja_indicadores_api.fotos.authentication.delivery import (
        FotosVerificationDeliveryService,
    )

    session = Mock()
    email_service = Mock()

    service = FotosVerificationDeliveryService(
        session,
        email_service,
    )

    service._repository = Mock()
    service._repository.update_delivery_status.side_effect = RuntimeError(
        "Falha simulada no banco."
    )

    with pytest.raises(RuntimeError, match="Falha simulada no banco"):
        service.deliver(
            verification_id="verificacao-001",
            recipient="usuario@exemplo.com",
            purpose=FotosVerificationPurpose.ACTIVATION,
            code="012345",
        )

    email_service.send.assert_called_once()

    service._repository.update_delivery_status.assert_called_once_with(
        "verificacao-001",
        "sent",
    )

    session.commit.assert_not_called()
    session.rollback.assert_called_once()


def test_delivery_service_rejects_unavailable_state() -> None:
    """Rejeita atualizacao quando a entrega nao esta pendente."""

    from unittest.mock import Mock

    from deja_indicadores_api.fotos.authentication.delivery import (
        FotosVerificationDeliveryService,
        FotosVerificationDeliveryStateError,
    )

    session = Mock()
    email_service = Mock()

    service = FotosVerificationDeliveryService(
        session,
        email_service,
    )

    service._repository = Mock()
    service._repository.update_delivery_status.return_value = False

    with pytest.raises(FotosVerificationDeliveryStateError):
        service.deliver(
            verification_id="verificacao-001",
            recipient="usuario@exemplo.com",
            purpose=FotosVerificationPurpose.ACTIVATION,
            code="012345",
        )

    email_service.send.assert_called_once()

    service._repository.update_delivery_status.assert_called_once_with(
        "verificacao-001",
        "sent",
    )

    session.commit.assert_not_called()
    session.rollback.assert_called_once()
