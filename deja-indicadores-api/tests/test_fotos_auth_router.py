"""Testes HTTP dos endpoints publicos de autenticacao Fotos."""

from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from deja_indicadores_api.fotos.authentication.dependencies import (
    get_fotos_verification_request_service,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.fotos.authentication.router import router


@pytest.fixture
def http_client():
    """Cria uma API isolada com o servico de solicitacao simulado."""

    app = FastAPI()
    app.include_router(router, prefix="/api")

    service = Mock()

    app.dependency_overrides[get_fotos_verification_request_service] = lambda: service

    with TestClient(app) as client:
        yield client, service


@pytest.mark.parametrize(
    ("endpoint", "purpose"),
    [
        (
            "/api/fotos/auth/activation/request",
            FotosVerificationPurpose.ACTIVATION,
        ),
        (
            "/api/fotos/auth/password-reset/request",
            FotosVerificationPurpose.PASSWORD_RESET,
        ),
    ],
)
def test_public_request_endpoints(
    http_client,
    endpoint: str,
    purpose: FotosVerificationPurpose,
) -> None:
    """Retorna resposta generica e encaminha os dados corretamente."""

    client, service = http_client

    response = client.post(
        endpoint,
        json={
            "organization_code": " cliente-a ",
            "email": "usuario@exemplo.com",
        },
    )

    assert response.status_code == 202

    body = response.json()

    assert "message" in body
    assert "codigo de verificacao" in body["message"]
    assert "012345" not in str(body)

    service.request_code.assert_called_once_with(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
        purpose=purpose,
        client_ip="testclient",
    )


def test_public_request_rejects_invalid_email(http_client) -> None:
    """Nao processa solicitacoes com e-mail invalido."""

    client, service = http_client

    response = client.post(
        "/api/fotos/auth/activation/request",
        json={
            "organization_code": "cliente-a",
            "email": "email-invalido",
        },
    )

    assert response.status_code == 422
    service.request_code.assert_not_called()
