from collections.abc import Mapping

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.module_management.models import (
    OrganizationModuleModel,
)
from tests.authentication.test_authentication_api import (
    create_organization,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)
from tests.module_management.test_authenticated_modules_api import (
    configure_organization_modules,
)

PROTECTED_ENDPOINTS = (
    (
        "indicators",
        "/api/indicators",
    ),
    (
        "measurements",
        "/api/measurements",
    ),
    (
        "reports",
        "/api/reports/management",
    ),
    (
        "indicators",
        "/api/dashboards/overview",
    ),
    (
        "chamados",
        "/api/chamados/clients",
    ),
)


def organization_administrator_headers(
    client: TestClient,
    settings: Settings,
    organization_id: str,
) -> Mapping[str, str]:
    """Cria um administrador organizacional autenticado."""

    administrator = create_user(
        client,
        organization_id,
        email="organization.admin@deja.com",
        role="organization_admin",
    )
    return authorization_headers(settings, administrator)


@pytest.mark.parametrize(
    ("module_key", "endpoint"),
    PROTECTED_ENDPOINTS,
)
def test_disabled_module_blocks_commercial_endpoint(
    client: TestClient,
    test_settings: Settings,
    module_key: str,
    endpoint: str,
) -> None:
    """Bloqueia o endpoint quando o módulo não está liberado."""

    organization = create_organization(
        client,
        enabled_modules=(),
    )
    headers = organization_administrator_headers(
        client,
        test_settings,
        str(organization["id"]),
    )

    response = client.get(endpoint, headers=headers)

    assert response.status_code == 403
    assert response.json() == {
        "error": "module_not_enabled",
        "message": (
            "O módulo solicitado não está liberado para esta "
            "organização."
        ),
    }


@pytest.mark.parametrize(
    ("module_key", "endpoint"),
    PROTECTED_ENDPOINTS,
)
def test_enabled_module_allows_commercial_endpoint(
    client: TestClient,
    test_settings: Settings,
    module_key: str,
    endpoint: str,
) -> None:
    """Permite o endpoint quando o módulo está liberado."""

    organization = create_organization(client)
    organization_id = str(organization["id"])
    configure_organization_modules(
        client,
        organization_id,
        {module_key},
    )
    headers = organization_administrator_headers(
        client,
        test_settings,
        organization_id,
    )

    response = client.get(endpoint, headers=headers)

    assert response.status_code == 200


@pytest.mark.parametrize(
    ("module_key", "endpoint"),
    PROTECTED_ENDPOINTS,
)
def test_platform_admin_bypasses_organization_module_check(
    client: TestClient,
    test_settings: Settings,
    module_key: str,
    endpoint: str,
) -> None:
    """Mantém a exceção administrativa do platform_admin."""

    administrator = create_user(
        client,
        None,
        email=f"platform.{module_key}@deja.com",
        role="platform_admin",
    )
    headers = authorization_headers(
        test_settings,
        administrator,
    )

    response = client.get(endpoint, headers=headers)

    assert response.status_code == 200


def test_module_deactivation_blocks_next_request(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Aplica uma desativação sem aguardar a expiração do JWT."""

    organization = create_organization(client)
    organization_id = str(organization["id"])
    configure_organization_modules(
        client,
        organization_id,
        {"indicators"},
    )
    headers = organization_administrator_headers(
        client,
        test_settings,
        organization_id,
    )

    first_response = client.get(
        "/api/indicators",
        headers=headers,
    )

    assert first_response.status_code == 200

    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        association = session.get(
            OrganizationModuleModel,
            (organization_id, "indicators"),
        )

        assert association is not None

        association.enabled = False
        session.commit()

    second_response = client.get(
        "/api/indicators",
        headers=headers,
    )

    assert second_response.status_code == 403
    assert (
        second_response.json()["error"]
        == "module_not_enabled"
    )