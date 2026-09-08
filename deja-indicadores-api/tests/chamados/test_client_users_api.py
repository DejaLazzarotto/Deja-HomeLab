from uuid import uuid4

from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)
from tests.chamados.clients.test_clients_api import (
    FIRST_CLIENT,
    create_client,
)

CLIENT_USERS_URL = "/api/chamados/client-users"


def create_context(
    client: TestClient,
    test_settings: Settings,
) -> dict[str, object]:
    """Cria hierarquia, administrador e ambiente para os testes."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )

    administrator = create_user(
        client,
        None,
        email=f"platform-admin-{uuid4()}@deja.com",
        role="platform_admin",
    )

    headers = authorization_headers(
        test_settings,
        administrator,
    )

    return {
        "organization": organization,
        "tenant": tenant,
        "environment": environment,
        "administrator": administrator,
        "headers": headers,
    }


def create_portal_user(
    client: TestClient,
    context: dict[str, object],
) -> dict[str, object]:
    """Cria um usuário externo no mesmo escopo do ambiente."""

    organization = context["organization"]
    tenant = context["tenant"]
    environment = context["environment"]

    assert isinstance(organization, dict)
    assert isinstance(tenant, dict)
    assert isinstance(environment, dict)

    return create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"portal-{uuid4()}@deja.com",
        role="client",
    )


def create_chamados_client(
    client: TestClient,
    context: dict[str, object],
    *,
    suffix: str = "",
) -> dict[str, object]:
    """Cria um Cliente do Chamados no ambiente do contexto."""

    environment = context["environment"]
    headers = context["headers"]

    assert isinstance(environment, dict)
    assert isinstance(headers, dict)

    payload = {
        **FIRST_CLIENT,
        "document": (
            f"{uuid4().int % 10**14:014d}"
        ),
        "email": f"cliente-{uuid4()}@deja.com",
        "company_name": (
            f"{FIRST_CLIENT['company_name']} {suffix}".strip()
        ),
        "fantasy_name": (
            f"{FIRST_CLIENT['fantasy_name']} {suffix}".strip()
        ),
    }

    return create_client(
        client,
        payload,
        str(environment["id"]),
        headers,
    )


def test_create_client_user_link(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Vincula um usuário client a um Cliente do Chamados."""

    context = create_context(
        client,
        test_settings,
    )

    portal_user = create_portal_user(
        client,
        context,
    )

    chamados_client = create_chamados_client(
        client,
        context,
    )

    headers = context["headers"]
    assert isinstance(headers, dict)

    response = client.post(
        CLIENT_USERS_URL,
        headers=headers,
        json={
            "user_id": str(portal_user["id"]),
            "client_id": str(chamados_client["id"]),
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["user_id"] == portal_user["id"]
    assert body["client_id"] == chamados_client["id"]
    assert body["created_at"]


def test_get_client_user_link(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Consulta o Cliente vinculado ao usuário."""

    context = create_context(
        client,
        test_settings,
    )

    portal_user = create_portal_user(
        client,
        context,
    )

    chamados_client = create_chamados_client(
        client,
        context,
    )

    headers = context["headers"]
    assert isinstance(headers, dict)

    create_response = client.post(
        CLIENT_USERS_URL,
        headers=headers,
        json={
            "user_id": str(portal_user["id"]),
            "client_id": str(chamados_client["id"]),
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"{CLIENT_USERS_URL}/{portal_user['id']}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_id"] == portal_user["id"]
    assert body["client_id"] == chamados_client["id"]


def test_client_user_requires_client_role(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Impede vínculo de usuários institucionais internos."""

    context = create_context(
        client,
        test_settings,
    )

    organization = context["organization"]
    tenant = context["tenant"]
    environment = context["environment"]
    headers = context["headers"]

    assert isinstance(organization, dict)
    assert isinstance(tenant, dict)
    assert isinstance(environment, dict)
    assert isinstance(headers, dict)

    internal_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"viewer-{uuid4()}@deja.com",
        role="viewer",
    )

    chamados_client = create_chamados_client(
        client,
        context,
    )

    response = client.post(
        CLIENT_USERS_URL,
        headers=headers,
        json={
            "user_id": str(internal_user["id"]),
            "client_id": str(chamados_client["id"]),
        },
    )

    assert response.status_code == 403


def test_client_user_requires_matching_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Exige que usuário e Cliente pertençam ao mesmo ambiente."""

    context = create_context(
        client,
        test_settings,
    )

    organization = context["organization"]
    tenant = context["tenant"]
    headers = context["headers"]

    assert isinstance(organization, dict)
    assert isinstance(tenant, dict)
    assert isinstance(headers, dict)

    second_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )

    portal_user = create_portal_user(
        client,
        context,
    )

    payload = {
        **FIRST_CLIENT,
        "document": f"{uuid4().int % 10**14:014d}",
        "email": f"cliente-{uuid4()}@deja.com",
    }

    chamados_client = create_client(
        client,
        payload,
        str(second_environment["id"]),
        headers,
    )

    response = client.post(
        CLIENT_USERS_URL,
        headers=headers,
        json={
            "user_id": str(portal_user["id"]),
            "client_id": str(chamados_client["id"]),
        },
    )

    assert response.status_code == 403


def test_client_user_cannot_have_multiple_links(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Impede mais de um Cliente vinculado ao mesmo usuário."""

    context = create_context(
        client,
        test_settings,
    )

    portal_user = create_portal_user(
        client,
        context,
    )

    client_a = create_chamados_client(
        client,
        context,
        suffix="A",
    )

    client_b = create_chamados_client(
        client,
        context,
        suffix="B",
    )

    headers = context["headers"]
    assert isinstance(headers, dict)

    first_response = client.post(
        CLIENT_USERS_URL,
        headers=headers,
        json={
            "user_id": str(portal_user["id"]),
            "client_id": str(client_a["id"]),
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        CLIENT_USERS_URL,
        headers=headers,
        json={
            "user_id": str(portal_user["id"]),
            "client_id": str(client_b["id"]),
        },
    )

    assert second_response.status_code == 409