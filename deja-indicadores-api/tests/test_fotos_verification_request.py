"""Testes do fluxo de solicitacao de codigos do Fotos PWA."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from deja_indicadores_api.fotos.authentication.issuance import (
    FotosVerificationCooldownError,
    FotosVerificationNotEligibleError,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.request import (
    FotosVerificationRequestService,
)


def build_request_service():
    """Prepara o fluxo com dependencias simuladas."""

    service = FotosVerificationRequestService(
        Mock(),
        Mock(),
        Mock(),
    )

    service._identity = Mock()
    service._issuance = Mock()
    service._delivery = Mock()

    return service


def test_request_code_ignores_unknown_user():
    """Nao emite nem envia codigo para conta desconhecida."""

    service = build_request_service()
    service._identity.find_user.return_value = None

    result = service.request_code(
        organization_code="cliente-a",
        email="desconhecido@exemplo.com",
        purpose=FotosVerificationPurpose.ACTIVATION,
    )

    assert result is None

    service._issuance.issue.assert_not_called()
    service._delivery.deliver.assert_not_called()


def test_request_code_delivers_to_registered_email():
    """Envia o codigo exclusivamente ao e-mail cadastrado."""

    service = build_request_service()

    service._identity.find_user.return_value = SimpleNamespace(
        id="usuario-001",
        email="cadastrado@exemplo.com",
    )

    service._issuance.issue.return_value = SimpleNamespace(
        verification_id="verificacao-001",
        code="012345",
    )

    service.request_code(
        organization_code="cliente-a",
        email="CADASTRADO@EXEMPLO.COM",
        purpose=FotosVerificationPurpose.ACTIVATION,
    )

    service._identity.find_user.assert_called_once_with(
        organization_code="cliente-a",
        email="CADASTRADO@EXEMPLO.COM",
    )

    service._issuance.issue.assert_called_once_with(
        user_id="usuario-001",
        purpose=FotosVerificationPurpose.ACTIVATION,
    )

    service._delivery.deliver.assert_called_once_with(
        verification_id="verificacao-001",
        recipient="cadastrado@exemplo.com",
        purpose=FotosVerificationPurpose.ACTIVATION,
        code="012345",
    )


@pytest.mark.parametrize(
    "error_type",
    [
        FotosVerificationNotEligibleError,
        FotosVerificationCooldownError,
    ],
)
def test_request_code_ignores_ineligible_or_cooldown(error_type):
    """Nao envia codigo quando emissao e recusada."""

    service = build_request_service()

    service._identity.find_user.return_value = SimpleNamespace(
        id="usuario-001",
        email="usuario@exemplo.com",
    )

    service._issuance.issue.side_effect = error_type()

    result = service.request_code(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
        purpose=FotosVerificationPurpose.PASSWORD_RESET,
    )

    assert result is None
    service._delivery.deliver.assert_not_called()


def test_request_code_hides_smtp_delivery_failure():
    """Nao revela a existencia da conta quando o SMTP falha."""

    from deja_indicadores_api.core.email import EmailDeliveryError

    service = build_request_service()

    service._identity.find_user.return_value = SimpleNamespace(
        id="usuario-001",
        email="usuario@exemplo.com",
    )

    service._issuance.issue.return_value = SimpleNamespace(
        verification_id="verificacao-001",
        code="012345",
    )

    service._delivery.deliver.side_effect = EmailDeliveryError("Falha simulada no SMTP.")

    result = service.request_code(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
        purpose=FotosVerificationPurpose.ACTIVATION,
    )

    assert result is None

    service._delivery.deliver.assert_called_once()


def test_request_code_blocks_before_user_lookup():
    """Nao consulta a identidade quando a requisicao excede o limite."""

    rate_limit = Mock()
    rate_limit.allow_request.return_value = False

    service = FotosVerificationRequestService(
        Mock(),
        Mock(),
        Mock(),
        rate_limit_service=rate_limit,
    )

    service._identity = Mock()
    service._issuance = Mock()
    service._delivery = Mock()

    result = service.request_code(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
        purpose=FotosVerificationPurpose.ACTIVATION,
        client_ip="192.0.2.10",
    )

    assert result is None

    rate_limit.allow_request.assert_called_once_with(
        client_ip="192.0.2.10",
        organization_code="cliente-a",
        email="usuario@exemplo.com",
    )

    service._identity.find_user.assert_not_called()
    service._issuance.issue.assert_not_called()
    service._delivery.deliver.assert_not_called()


def test_request_code_continues_when_rate_limit_allows():
    """Consulta o usuario normalmente quando a requisicao e permitida."""

    rate_limit = Mock()
    rate_limit.allow_request.return_value = True

    service = FotosVerificationRequestService(
        Mock(),
        Mock(),
        Mock(),
        rate_limit_service=rate_limit,
    )

    service._identity = Mock()
    service._issuance = Mock()
    service._delivery = Mock()

    service._identity.find_user.return_value = None

    result = service.request_code(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
        purpose=FotosVerificationPurpose.PASSWORD_RESET,
        client_ip="192.0.2.11",
    )

    assert result is None

    rate_limit.allow_request.assert_called_once_with(
        client_ip="192.0.2.11",
        organization_code="cliente-a",
        email="usuario@exemplo.com",
    )

    service._identity.find_user.assert_called_once_with(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
    )

    service._issuance.issue.assert_not_called()
    service._delivery.deliver.assert_not_called()
