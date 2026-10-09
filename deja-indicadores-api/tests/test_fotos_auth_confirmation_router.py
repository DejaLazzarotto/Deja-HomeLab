"""Testes HTTP da confirmacao publica de codigos do Fotos PWA."""

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from deja_indicadores_api.fotos.authentication.confirmation import (
    FotosVerificationInvalidCodeError,
)
from deja_indicadores_api.fotos.authentication.dependencies import (
    get_fotos_verification_confirmation_service,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.router import router


@pytest.fixture
def confirmation_client():
    """Prepara uma API isolada com a confirmacao simulada."""

    app = FastAPI()
    app.include_router(router, prefix="/api")

    service = Mock()

    app.dependency_overrides[get_fotos_verification_confirmation_service] = lambda: service

    with TestClient(app) as client:
        yield client, service


@pytest.mark.parametrize(
    ("endpoint", "purpose"),
    [
        (
            "/api/fotos/auth/activation/confirm",
            FotosVerificationPurpose.ACTIVATION,
        ),
        (
            "/api/fotos/auth/password-reset/confirm",
            FotosVerificationPurpose.PASSWORD_RESET,
        ),
    ],
)
def test_confirmation_endpoints_return_success(
    confirmation_client,
    endpoint: str,
    purpose: FotosVerificationPurpose,
) -> None:
    """Confirma a senha e encaminha a finalidade correta."""

    client, service = confirmation_client

    response = client.post(
        endpoint,
        json={
            "organization_code": " cliente-a ",
            "email": "usuario@exemplo.com",
            "code": "001234",
            "new_password": "SenhaSegura123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Senha definida com sucesso."}

    service.confirm.assert_called_once_with(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
        purpose=purpose,
        code="001234",
        new_password="SenhaSegura123",
        client_ip="testclient",
    )


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/fotos/auth/activation/confirm",
        "/api/fotos/auth/password-reset/confirm",
    ],
)
def test_confirmation_endpoints_hide_invalid_code(
    confirmation_client,
    endpoint: str,
) -> None:
    """Retorna erro generico sem revelar detalhes da conta."""

    client, service = confirmation_client
    service.confirm.side_effect = FotosVerificationInvalidCodeError()

    response = client.post(
        endpoint,
        json={
            "organization_code": "cliente-a",
            "email": "usuario@exemplo.com",
            "code": "123456",
            "new_password": "SenhaSegura123",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Codigo invalido ou expirado. Solicite um novo codigo."}


def test_confirmation_rejects_invalid_code_format(
    confirmation_client,
) -> None:
    """Nao chama o servico quando o codigo possui formato invalido."""

    client, service = confirmation_client

    response = client.post(
        "/api/fotos/auth/activation/confirm",
        json={
            "organization_code": "cliente-a",
            "email": "usuario@exemplo.com",
            "code": "12345",
            "new_password": "SenhaSegura123",
        },
    )

    assert response.status_code == 422
    service.confirm.assert_not_called()
