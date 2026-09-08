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
PORTAL_TICKETS_URL = "/api/chamados/portal/tickets"
TICKETS_URL = "/api/chamados/tickets"


def create_portal_context(
    client: TestClient,
    test_settings: Settings,
) -> dict[str, object]:
    """Cria Cliente, usuário externo vinculado e credenciais de Portal."""

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

    administrator_headers = authorization_headers(
        test_settings,
        administrator,
    )

    chamados_client = create_client(
        client,
        {
            **FIRST_CLIENT,
            "document": f"{uuid4().int % 10**14:014d}",
            "email": f"cliente-{uuid4()}@deja.com",
        },
        str(environment["id"]),
        administrator_headers,
    )

    portal_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"portal-{uuid4()}@deja.com",
        role="client",
    )

    link_response = client.post(
        CLIENT_USERS_URL,
        headers=administrator_headers,
        json={
            "user_id": str(portal_user["id"]),
            "client_id": str(chamados_client["id"]),
        },
    )

    assert link_response.status_code == 201

    portal_headers = authorization_headers(
        test_settings,
        portal_user,
    )

    return {
        "organization": organization,
        "tenant": tenant,
        "environment": environment,
        "administrator": administrator,
        "administrator_headers": administrator_headers,
        "client": chamados_client,
        "portal_user": portal_user,
        "portal_headers": portal_headers,
    }


def test_portal_opens_ticket_with_derived_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Portal deriva Cliente, escopo, prioridade e autoria."""

    context = create_portal_context(
        client,
        test_settings,
    )

    portal_headers = context["portal_headers"]

    assert isinstance(portal_headers, dict)

    response = client.post(
        PORTAL_TICKETS_URL,
        headers=portal_headers,
        json={
            "title": " Problema no acesso ",
            "description": " Não consigo acessar o sistema. ",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["title"] == "Problema no acesso"
    assert body["description"] == "Não consigo acessar o sistema."
    assert body["status"] == "open"
    assert body["priority"] == "medium"
    assert body["assigned_to_user_name"] is None
    assert body["closed_at"] is None

    assert "organization_id" not in body
    assert "tenant_id" not in body
    assert "environment_id" not in body
    assert "client_id" not in body
    assert "opened_by_user_id" not in body
    assert "assigned_to_user_id" not in body
    assert "closed_by_user_id" not in body


def test_portal_lists_only_linked_client_tickets(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Usuário externo lista somente chamados de seu Cliente."""

    context = create_portal_context(
        client,
        test_settings,
    )

    portal_headers = context["portal_headers"]
    administrator_headers = context["administrator_headers"]
    environment = context["environment"]

    assert isinstance(portal_headers, dict)
    assert isinstance(administrator_headers, dict)
    assert isinstance(environment, dict)

    own_ticket_response = client.post(
        PORTAL_TICKETS_URL,
        headers=portal_headers,
        json={
            "title": "Chamado do Portal",
            "description": "Chamado pertencente ao cliente autenticado.",
        },
    )

    assert own_ticket_response.status_code == 201
    own_ticket = own_ticket_response.json()

    other_client = create_client(
        client,
        {
            **FIRST_CLIENT,
            "document": f"{uuid4().int % 10**14:014d}",
            "email": f"outro-cliente-{uuid4()}@deja.com",
            "company_name": "Outra Empresa Ltda",
            "fantasy_name": "Outra Empresa",
        },
        str(environment["id"]),
        administrator_headers,
    )

    other_ticket_response = client.post(
        TICKETS_URL,
        headers=administrator_headers,
        json={
            "environment_id": str(environment["id"]),
            "client_id": str(other_client["id"]),
            "title": "Chamado de outro Cliente",
            "description": "Não pode aparecer no Portal.",
            "priority": "medium",
            "assigned_to_user_id": None,
        },
    )

    assert other_ticket_response.status_code == 201

    response = client.get(
        PORTAL_TICKETS_URL,
        headers=portal_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert [ticket["id"] for ticket in body] == [
        own_ticket["id"],
    ]


def test_portal_cannot_read_other_client_ticket(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Impede consulta direta de chamado pertencente a outro Cliente."""

    context = create_portal_context(
        client,
        test_settings,
    )

    portal_headers = context["portal_headers"]
    administrator_headers = context["administrator_headers"]
    environment = context["environment"]

    assert isinstance(portal_headers, dict)
    assert isinstance(administrator_headers, dict)
    assert isinstance(environment, dict)

    other_client = create_client(
        client,
        {
            **FIRST_CLIENT,
            "document": f"{uuid4().int % 10**14:014d}",
            "email": f"outro-cliente-{uuid4()}@deja.com",
            "company_name": "Empresa Externa Ltda",
            "fantasy_name": "Empresa Externa",
        },
        str(environment["id"]),
        administrator_headers,
    )

    other_ticket_response = client.post(
        TICKETS_URL,
        headers=administrator_headers,
        json={
            "environment_id": str(environment["id"]),
            "client_id": str(other_client["id"]),
            "title": "Chamado privado",
            "description": "Pertence a outro Cliente.",
            "priority": "high",
            "assigned_to_user_id": None,
        },
    )

    assert other_ticket_response.status_code == 201

    other_ticket = other_ticket_response.json()

    response = client.get(
        f"{PORTAL_TICKETS_URL}/{other_ticket['id']}",
        headers=portal_headers,
    )

    assert response.status_code == 403


def test_internal_user_cannot_use_portal(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Impede usuários internos de utilizarem endpoints do Portal."""

    organization = create_organization(client)

    tenant = create_tenant(
        client,
        str(organization["id"]),
    )

    environment = create_environment(
        client,
        str(tenant["id"]),
    )

    viewer = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"viewer-{uuid4()}@deja.com",
        role="viewer",
    )

    headers = authorization_headers(
        test_settings,
        viewer,
    )

    response = client.get(
        PORTAL_TICKETS_URL,
        headers=headers,
    )

    assert response.status_code == 403


def test_unlinked_client_user_cannot_use_portal(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Exige vínculo com um Cliente antes de liberar o Portal."""

    organization = create_organization(client)

    tenant = create_tenant(
        client,
        str(organization["id"]),
    )

    environment = create_environment(
        client,
        str(tenant["id"]),
    )

    portal_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"portal-sem-cliente-{uuid4()}@deja.com",
        role="client",
    )

    headers = authorization_headers(
        test_settings,
        portal_user,
    )

    response = client.get(
        PORTAL_TICKETS_URL,
        headers=headers,
    )

    assert response.status_code == 404