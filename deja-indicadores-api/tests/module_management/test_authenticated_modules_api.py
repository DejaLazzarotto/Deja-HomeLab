from collections.abc import Collection, Mapping

from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.module_management.models import (
    OrganizationModuleModel,
)
from tests.authentication.test_authentication_api import (
    INITIAL_MODULES,
    create_organization,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)

ME_URL = "/api/v1/auth/me"


def configure_organization_modules(
    client: TestClient,
    organization_id: str,
    enabled_keys: Collection[str],
) -> None:
    """Atualiza os estados dos módulos da organização de teste."""

    enabled_key_set = set(enabled_keys)
    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        for module_data in INITIAL_MODULES:
            module_key = str(module_data["key"])
            association = session.get(
                OrganizationModuleModel,
                (organization_id, module_key),
            )

            assert association is not None

            association.enabled = (
                module_key in enabled_key_set
            )

        session.commit()

def organization_user_headers(
    client: TestClient,
    settings: Settings,
    organization_id: str,
) -> Mapping[str, str]:
    """Cria um administrador da organização autenticado."""

    user = create_user(
        client,
        organization_id,
        email="organization.admin@deja.com",
        role="organization_admin",
    )
    return authorization_headers(settings, user)


def test_me_returns_enabled_organization_modules(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Expõe na sessão somente os módulos habilitados."""

    organization = create_organization(client)
    organization_id = str(organization["id"])
    configure_organization_modules(
        client,
        organization_id,
        {
            "indicators",
            "reports",
        },
    )
    headers = organization_user_headers(
        client,
        test_settings,
        organization_id,
    )

    response = client.get(ME_URL, headers=headers)

    assert response.status_code == 200
    assert response.json()["enabled_modules"] == [
        "indicators",
        "reports",
    ]


def test_me_reflects_module_change_on_next_request(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Atualiza os módulos sem aguardar a expiração do JWT."""

    organization = create_organization(client)
    organization_id = str(organization["id"])
    configure_organization_modules(
        client,
        organization_id,
        {"indicators"},
    )
    headers = organization_user_headers(
        client,
        test_settings,
        organization_id,
    )

    first_response = client.get(ME_URL, headers=headers)

    assert first_response.status_code == 200
    assert first_response.json()["enabled_modules"] == [
        "indicators"
    ]

    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        indicators = session.get(
            OrganizationModuleModel,
            (organization_id, "indicators"),
        )
        reports = session.get(
            OrganizationModuleModel,
            (organization_id, "reports"),
        )

        assert indicators is not None
        assert reports is not None

        indicators.enabled = False
        reports.enabled = True
        session.commit()

    second_response = client.get(ME_URL, headers=headers)

    assert second_response.status_code == 200
    assert second_response.json()["enabled_modules"] == [
        "reports"
    ]


def test_platform_admin_has_empty_enabled_modules(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Mantém vazia a lista do administrador global sem organização."""

    administrator = create_user(
        client,
        None,
        email="platform.admin@deja.com",
        role="platform_admin",
    )
    headers = authorization_headers(
        test_settings,
        administrator,
    )

    response = client.get(ME_URL, headers=headers)

    assert response.status_code == 200
    assert response.json()["role"] == "platform_admin"
    assert response.json()["organization_id"] is None
    assert response.json()["enabled_modules"] == []