from collections.abc import Mapping

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.module_management.models import ModuleModel
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    assert_access_forbidden,
    authorization_headers,
)

MODULES_URL = "/api/v1/modules"


INITIAL_MODULES = (
    {
        "key": "indicators",
        "name": "Indicadores",
        "description": (
            "Gestão de indicadores e visão geral no dashboard."
        ),
        "display_order": 10,
    },
    {
        "key": "measurements",
        "name": "Coleta Manual",
        "description": (
            "Lançamento e gerenciamento manual de medições."
        ),
        "display_order": 20,
    },
    {
        "key": "reports",
        "name": "Relatórios Gerenciais",
        "description": (
            "Consulta e emissão de relatórios gerenciais."
        ),
        "display_order": 30,
    },
)


def create_catalog(client: TestClient) -> None:
    """Insere o catálogo inicial diretamente no banco de testes."""

    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add_all(
            [
                ModuleModel(**module_data)
                for module_data in INITIAL_MODULES
            ]
        )
        session.commit()


def platform_administrator_headers(
    client: TestClient,
    settings: Settings,
) -> Mapping[str, str]:
    """Cria um administrador global autenticado."""

    administrator = create_user(
        client,
        None,
        email="platform.admin@deja.com",
        role="platform_admin",
    )
    return authorization_headers(settings, administrator)


def organization_modules_url(organization_id: object) -> str:
    """Monta a URL administrativa dos módulos da organização."""

    return f"/api/v1/organizations/{organization_id}/modules"


def enabled_module_keys(
    response_body: dict[str, object],
) -> set[str]:
    """Extrai as chaves habilitadas de uma resposta organizacional."""

    modules = response_body["modules"]

    assert isinstance(modules, list)

    return {
        str(module["key"])
        for module in modules
        if isinstance(module, dict) and module["enabled"]
    }


def test_module_catalog_requires_bearer_token(
    client: TestClient,
) -> None:
    """Protege o catálogo com autenticação."""

    response = client.get(MODULES_URL)

    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_access_token",
        "message": "Token de acesso inválido.",
    }


def test_platform_admin_lists_installed_catalog(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Lista o catálogo instalado na ordem de apresentação."""

    create_catalog(client)
    headers = platform_administrator_headers(
        client,
        test_settings,
    )

    response = client.get(
        MODULES_URL,
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert [module["key"] for module in body] == [
        "indicators",
        "measurements",
        "reports",
    ]
    assert [module["display_order"] for module in body] == [
        10,
        20,
        30,
    ]
    assert all(module["created_at"] for module in body)
    assert all(module["updated_at"] for module in body)


@pytest.mark.parametrize(
    "role",
    [
        "organization_admin",
        "tenant_admin",
        "manager",
        "analyst",
        "viewer",
    ],
)
def test_non_platform_roles_cannot_manage_modules(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Nega o controle comercial a todos os demais papéis."""

    organization = create_organization(client)
    tenant_id: str | None = None
    environment_id: str | None = None

    if role != "organization_admin":
        tenant = create_tenant(
            client,
            str(organization["id"]),
        )
        tenant_id = str(tenant["id"])

    if role in {"manager", "analyst", "viewer"}:
        environment = create_environment(
            client,
            str(tenant_id),
        )
        environment_id = str(environment["id"])

    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=tenant_id,
        environment_id=environment_id,
        email=f"{role}@deja.com",
        role=role,
    )

    response = client.get(
        MODULES_URL,
        headers=authorization_headers(test_settings, user),
    )

    assert_access_forbidden(response)


def test_new_organization_has_all_modules_disabled(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Interpreta a ausência de associações como módulo não liberado."""

    create_catalog(client)
    organization = create_organization(
        client,
        enabled_modules=(),
    )
    headers = platform_administrator_headers(
        client,
        test_settings,
    )

    response = client.get(
        organization_modules_url(organization["id"]),
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["organization_id"] == organization["id"]
    assert [module["key"] for module in body["modules"]] == [
        "indicators",
        "measurements",
        "reports",
    ]
    assert enabled_module_keys(body) == set()


def test_platform_admin_replaces_organization_modules(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Substitui integralmente a seleção de módulos."""

    create_catalog(client)
    organization = create_organization(client)
    headers = platform_administrator_headers(
        client,
        test_settings,
    )
    url = organization_modules_url(organization["id"])

    first_response = client.put(
        url,
        json={
            "enabled_modules": [
                "indicators",
                "measurements",
            ]
        },
        headers=headers,
    )

    assert first_response.status_code == 200
    assert enabled_module_keys(first_response.json()) == {
        "indicators",
        "measurements",
    }

    second_response = client.put(
        url,
        json={"enabled_modules": ["reports"]},
        headers=headers,
    )

    assert second_response.status_code == 200
    assert enabled_module_keys(second_response.json()) == {
        "reports"
    }


def test_unknown_module_key_does_not_change_selection(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita chave desconhecida antes de alterar as associações."""

    create_catalog(client)
    organization = create_organization(client)
    headers = platform_administrator_headers(
        client,
        test_settings,
    )
    url = organization_modules_url(organization["id"])

    initial_response = client.put(
        url,
        json={"enabled_modules": ["indicators"]},
        headers=headers,
    )

    assert initial_response.status_code == 200

    invalid_response = client.put(
        url,
        json={
            "enabled_modules": [
                "reports",
                "unknown_module",
            ]
        },
        headers=headers,
    )

    assert invalid_response.status_code == 400
    assert invalid_response.json()["error"] == "unknown_module_keys"

    persisted_response = client.get(
        url,
        headers=headers,
    )

    assert persisted_response.status_code == 200
    assert enabled_module_keys(persisted_response.json()) == {
        "indicators"
    }


def test_duplicate_module_key_is_rejected(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita uma seleção que repete a mesma chave."""

    create_catalog(client)
    organization = create_organization(client)
    headers = platform_administrator_headers(
        client,
        test_settings,
    )

    response = client.put(
        organization_modules_url(organization["id"]),
        json={
            "enabled_modules": [
                "indicators",
                "indicators",
            ]
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_unknown_organization_returns_not_found(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Retorna erro ao consultar liberações de organização inexistente."""

    create_catalog(client)
    headers = platform_administrator_headers(
        client,
        test_settings,
    )
    organization_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        organization_modules_url(organization_id),
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "organization_not_found"


def test_module_selections_are_isolated_between_organizations(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Mantém liberações independentes para cada organização."""

    create_catalog(client)
    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )
    headers = platform_administrator_headers(
        client,
        test_settings,
    )
    first_url = organization_modules_url(
        first_organization["id"]
    )
    second_url = organization_modules_url(
        second_organization["id"]
    )

    first_update = client.put(
        first_url,
        json={"enabled_modules": ["indicators"]},
        headers=headers,
    )
    second_update = client.put(
        second_url,
        json={"enabled_modules": ["reports"]},
        headers=headers,
    )

    assert first_update.status_code == 200
    assert second_update.status_code == 200

    first_response = client.get(first_url, headers=headers)
    second_response = client.get(second_url, headers=headers)

    assert enabled_module_keys(first_response.json()) == {
        "indicators"
    }
    assert enabled_module_keys(second_response.json()) == {
        "reports"
    }