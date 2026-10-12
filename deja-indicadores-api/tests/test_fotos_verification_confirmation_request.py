"""Testes da coordenacao da confirmacao publica do Fotos PWA."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from deja_indicadores_api.fotos.authentication.confirmation import (
    FotosVerificationInvalidCodeError,
)
from deja_indicadores_api.fotos.authentication.confirmation_request import (
    FotosVerificationConfirmationRequestService,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)


def build_confirmation_request_service():
    """Prepara o servico com dependencias simuladas."""

    service = FotosVerificationConfirmationRequestService(
        session=Mock(),
        code_service=Mock(),
        password_service=Mock(),
    )

    service._identity = Mock()
    service._confirmation = Mock()

    return service


def test_confirmation_rejects_unknown_account():
    """Conta inexistente recebe o mesmo erro de codigo invalido."""

    service = build_confirmation_request_service()
    service._identity.find_user.return_value = None

    with pytest.raises(FotosVerificationInvalidCodeError):
        service.confirm(
            organization_code="cliente-a",
            email="desconhecido@exemplo.com",
            purpose=FotosVerificationPurpose.ACTIVATION,
            code="123456",
            new_password="SenhaSegura123",
        )

    service._identity.find_user.assert_called_once_with(
        organization_code="cliente-a",
        email="desconhecido@exemplo.com",
    )

    service._confirmation.confirm.assert_not_called()


@pytest.mark.parametrize(
    "purpose",
    [
        FotosVerificationPurpose.ACTIVATION,
        FotosVerificationPurpose.PASSWORD_RESET,
    ],
)
def test_confirmation_uses_user_from_correct_organization(
    purpose: FotosVerificationPurpose,
):
    """Encaminha o usuario identificado dentro de sua organizacao."""

    service = build_confirmation_request_service()

    service._identity.find_user.return_value = SimpleNamespace(
        id="usuario-001",
    )

    service.confirm(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
        purpose=purpose,
        code="012345",
        new_password="SenhaSegura123",
    )

    service._identity.find_user.assert_called_once_with(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
    )

    service._confirmation.confirm.assert_called_once_with(
        user_id="usuario-001",
        purpose=purpose,
        code="012345",
        new_password="SenhaSegura123",
    )


def test_confirmation_rate_limit_blocks_before_identity():
    """Bloqueia a confirmacao antes de identificar o usuario."""

    rate_limit = Mock()
    rate_limit.allow_confirmation.return_value = False

    service = FotosVerificationConfirmationRequestService(
        session=Mock(),
        code_service=Mock(),
        password_service=Mock(),
        rate_limit_service=rate_limit,
    )

    service._identity = Mock()
    service._confirmation = Mock()

    with pytest.raises(FotosVerificationInvalidCodeError):
        service.confirm(
            organization_code="cliente-a",
            email="usuario@exemplo.com",
            purpose=FotosVerificationPurpose.ACTIVATION,
            code="123456",
            new_password="SenhaSegura123",
            client_ip="192.0.2.10",
        )

    rate_limit.allow_confirmation.assert_called_once_with(
        client_ip="192.0.2.10",
        organization_code="cliente-a",
        email="usuario@exemplo.com",
    )

    service._identity.find_user.assert_not_called()
    service._confirmation.confirm.assert_not_called()


def test_confirmation_rate_limit_allows_identity_lookup():
    """Continua a identificacao quando o limite permite confirmar."""

    rate_limit = Mock()
    rate_limit.allow_confirmation.return_value = True

    service = FotosVerificationConfirmationRequestService(
        session=Mock(),
        code_service=Mock(),
        password_service=Mock(),
        rate_limit_service=rate_limit,
    )

    service._identity = Mock()
    service._confirmation = Mock()

    service._identity.find_user.return_value = SimpleNamespace(
        id="usuario-001",
    )

    service.confirm(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
        purpose=FotosVerificationPurpose.PASSWORD_RESET,
        code="012345",
        new_password="SenhaSegura123",
        client_ip="192.0.2.11",
    )

    rate_limit.allow_confirmation.assert_called_once_with(
        client_ip="192.0.2.11",
        organization_code="cliente-a",
        email="usuario@exemplo.com",
    )

    service._identity.find_user.assert_called_once_with(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
    )

    service._confirmation.confirm.assert_called_once_with(
        user_id="usuario-001",
        purpose=FotosVerificationPurpose.PASSWORD_RESET,
        code="012345",
        new_password="SenhaSegura123",
    )
