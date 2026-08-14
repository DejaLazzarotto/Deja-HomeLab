from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from deja_indicadores_api import main as main_module
from deja_indicadores_api.core.config import Settings


def test_health_check_returns_ok(client: TestClient) -> None:
    """Confirma que a API está disponível."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_documentation_is_available_outside_production(
    monkeypatch: MonkeyPatch,
    test_settings: Settings,
) -> None:
    """Mantém a documentação acessível em testes e desenvolvimento."""

    monkeypatch.setattr(
        main_module,
        "get_settings",
        lambda: test_settings,
    )

    with TestClient(main_module.create_app()) as test_client:
        for path in (
            "/docs",
            "/docs/oauth2-redirect",
            "/openapi.json",
            "/redoc",
        ):
            response = test_client.get(path)

            assert response.status_code == 200


def test_api_documentation_is_disabled_in_production(
    monkeypatch: MonkeyPatch,
    test_settings: Settings,
) -> None:
    """Impede a exposição pública da documentação em produção."""

    production_settings = test_settings.model_copy(
        update={"app_env": "production"}
    )
    monkeypatch.setattr(
        main_module,
        "get_settings",
        lambda: production_settings,
    )

    with TestClient(main_module.create_app()) as test_client:
        health_response = test_client.get("/health")

        assert health_response.status_code == 200
        assert health_response.json() == {"status": "ok"}

        for path in (
            "/docs",
            "/docs/oauth2-redirect",
            "/openapi.json",
            "/redoc",
        ):
            response = test_client.get(path)

            assert response.status_code == 404
