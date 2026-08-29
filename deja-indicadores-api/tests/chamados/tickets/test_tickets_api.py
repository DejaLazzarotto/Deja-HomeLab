from collections.abc import Mapping
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import authorization_headers
from tests.chamados.clients.test_clients_api import FIRST_CLIENT, create_client

TICKETS_URL = "/api/chamados/tickets"


@pytest.fixture()
def ticket_context(
    client: TestClient,
    test_settings: Settings,
) -> dict[str, object]:
    """Cria hierarquia, Cliente, responsável e identidade global."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    administrator = create_user(
        client,
        None,
        email="platform.admin.chamados.tickets@deja.com",
        role="platform_admin",
    )
    headers = authorization_headers(test_settings, administrator)
    chamados_client = create_client(
        client,
        FIRST_CLIENT,
        str(environment["id"]),
        headers,
    )
    analyst = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="analista.chamados@deja.com",
        role="analyst",
    )

    return {
        "organization": organization,
        "tenant": tenant,
        "environment": environment,
        "administrator": administrator,
        "headers": headers,
        "client": chamados_client,
        "analyst": analyst,
    }


def ticket_payload(
    context: dict[str, object],
    **overrides: object,
) -> dict[str, object]:
    """Monta um chamado válido com substituições opcionais."""

    environment = context["environment"]
    chamados_client = context["client"]

    assert isinstance(environment, dict)
    assert isinstance(chamados_client, dict)

    return {
        "environment_id": str(environment["id"]),
        "client_id": str(chamados_client["id"]),
        "title": " Falha no acesso ao sistema ",
        "description": " Usuário não consegue acessar o sistema. ",
        "priority": "high",
        "assigned_to_user_id": None,
        **overrides,
    }


def create_ticket(
    client: TestClient,
    context: dict[str, object],
    *,
    headers: Mapping[str, str] | None = None,
    **overrides: object,
) -> dict[str, object]:
    """Abre um chamado e retorna o corpo da resposta."""

    effective_headers = headers or context["headers"]
    assert isinstance(effective_headers, Mapping)

    response = client.post(
        TICKETS_URL,
        json=ticket_payload(context, **overrides),
        headers=effective_headers,
    )

    assert response.status_code == 201
    return response.json()


def test_create_ticket_normalizes_and_derives_scope(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """A abertura deriva o escopo do Cliente e registra a autoria."""

    analyst = ticket_context["analyst"]
    administrator = ticket_context["administrator"]
    organization = ticket_context["organization"]
    tenant = ticket_context["tenant"]
    environment = ticket_context["environment"]
    chamados_client = ticket_context["client"]

    for value in (
        analyst,
        administrator,
        organization,
        tenant,
        environment,
        chamados_client,
    ):
        assert isinstance(value, dict)

    response = client.post(
        TICKETS_URL,
        json=ticket_payload(
            ticket_context,
            assigned_to_user_id=str(analyst["id"]),
        ),
        headers=ticket_context["headers"],
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["id"]) == 36
    assert body["organization_id"] == organization["id"]
    assert body["tenant_id"] == tenant["id"]
    assert body["environment_id"] == environment["id"]
    assert body["client_id"] == chamados_client["id"]
    assert body["title"] == "Falha no acesso ao sistema"
    assert body["description"] == "Usuário não consegue acessar o sistema."
    assert body["status"] == "open"
    assert body["priority"] == "high"
    assert body["opened_by_user_id"] == administrator["id"]
    assert body["assigned_to_user_id"] == analyst["id"]
    assert body["assigned_to_user_name"] == analyst["name"]
    assert body["closed_by_user_id"] is None
    assert body["closed_at"] is None


def test_list_tickets_applies_operational_filters(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """A listagem filtra por busca, estado, prioridade e Cliente."""

    first_ticket = create_ticket(client, ticket_context)
    assert first_ticket["assigned_to_user_name"] is None
    second_ticket = create_ticket(
        client,
        ticket_context,
        title="Impressora sem comunicação",
        description="Equipamento do financeiro está desconectado.",
        priority="low",
    )

    close_response = client.patch(
        f"{TICKETS_URL}/{second_ticket['id']}/status",
        json={"status": "closed"},
        headers=ticket_context["headers"],
    )
    assert close_response.status_code == 200

    chamados_client = ticket_context["client"]
    assert isinstance(chamados_client, dict)

    response = client.get(
        TICKETS_URL,
        params={
            "search": "acesso",
            "status": "open",
            "priority": "high",
            "client_id": chamados_client["id"],
        },
        headers=ticket_context["headers"],
    )

    assert response.status_code == 200
    assert [ticket["id"] for ticket in response.json()] == [first_ticket["id"]]


def test_get_ticket_by_id(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """Um chamado existente pode ser consultado pelo UUID."""

    ticket = create_ticket(client, ticket_context)

    response = client.get(
        f"{TICKETS_URL}/{ticket['id']}",
        headers=ticket_context["headers"],
    )

    assert response.status_code == 200
    assert response.json() == ticket


def test_update_ticket_operational_data(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """A atualização altera conteúdo, prioridade e responsável."""

    ticket = create_ticket(client, ticket_context)
    analyst = ticket_context["analyst"]
    assert isinstance(analyst, dict)

    response = client.put(
        f"{TICKETS_URL}/{ticket['id']}",
        json={
            "title": " Acesso restabelecido parcialmente ",
            "description": " A equipe segue monitorando o serviço. ",
            "priority": "critical",
            "assigned_to_user_id": analyst["id"],
        },
        headers=ticket_context["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Acesso restabelecido parcialmente"
    assert body["description"] == "A equipe segue monitorando o serviço."
    assert body["priority"] == "critical"
    assert body["assigned_to_user_id"] == analyst["id"]
    assert body["assigned_to_user_name"] == analyst["name"]
    assert body["client_id"] == ticket["client_id"]
    assert body["status"] == "open"


def test_close_and_reopen_ticket(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """Encerramento e reabertura mantêm as datas coerentes."""

    ticket = create_ticket(client, ticket_context)
    administrator = ticket_context["administrator"]
    assert isinstance(administrator, dict)

    close_response = client.patch(
        f"{TICKETS_URL}/{ticket['id']}/status",
        json={"status": "closed"},
        headers=ticket_context["headers"],
    )

    assert close_response.status_code == 200
    closed_ticket = close_response.json()
    assert closed_ticket["status"] == "closed"
    assert closed_ticket["closed_by_user_id"] == administrator["id"]
    assert closed_ticket["closed_at"] is not None

    reopen_response = client.patch(
        f"{TICKETS_URL}/{ticket['id']}/status",
        json={"status": "open"},
        headers=ticket_context["headers"],
    )

    assert reopen_response.status_code == 200
    reopened_ticket = reopen_response.json()
    assert reopened_ticket["status"] == "open"
    assert reopened_ticket["closed_by_user_id"] is None
    assert reopened_ticket["closed_at"] is None


def test_closed_ticket_rejects_transition_to_pending(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """Chamado encerrado precisa ser reaberto antes de ficar pendente."""

    ticket = create_ticket(client, ticket_context)
    close_response = client.patch(
        f"{TICKETS_URL}/{ticket['id']}/status",
        json={"status": "closed"},
        headers=ticket_context["headers"],
    )
    assert close_response.status_code == 200

    response = client.patch(
        f"{TICKETS_URL}/{ticket['id']}/status",
        json={"status": "pending"},
        headers=ticket_context["headers"],
    )

    assert response.status_code == 409
    assert response.json()["error"] == "chamados_ticket_invalid_status_transition"


def test_inactive_client_cannot_receive_ticket(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """Cliente inativo preserva histórico, mas não recebe novas aberturas."""

    chamados_client = ticket_context["client"]
    environment = ticket_context["environment"]
    assert isinstance(chamados_client, dict)
    assert isinstance(environment, dict)

    inactive_payload = {
        "environment_id": environment["id"],
        "company_name": chamados_client["company_name"],
        "fantasy_name": chamados_client["fantasy_name"],
        "document": chamados_client["document"],
        "contact_name": chamados_client["contact_name"],
        "phone": chamados_client["phone"],
        "whatsapp": chamados_client["whatsapp"],
        "email": chamados_client["email"],
        "city": chamados_client["city"],
        "state": chamados_client["state"],
        "notes": chamados_client["notes"],
        "active": False,
    }
    update_response = client.put(
        f"/api/chamados/clients/{chamados_client['id']}",
        json=inactive_payload,
        headers=ticket_context["headers"],
    )
    assert update_response.status_code == 200

    response = client.post(
        TICKETS_URL,
        json=ticket_payload(ticket_context),
        headers=ticket_context["headers"],
    )

    assert response.status_code == 409
    assert response.json()["error"] == "chamados_ticket_inactive_client"


def test_assigned_user_must_belong_to_ticket_scope(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """Responsável de outra organização não pode receber o chamado."""

    other_organization = create_organization(
        client,
        name="Outra Organização",
        code="OUTRA-ORG",
    )
    other_tenant = create_tenant(client, str(other_organization["id"]))
    other_environment = create_environment(client, str(other_tenant["id"]))
    other_analyst = create_user(
        client,
        str(other_organization["id"]),
        tenant_id=str(other_tenant["id"]),
        environment_id=str(other_environment["id"]),
        email="analista.outra.organizacao@deja.com",
        role="analyst",
    )

    response = client.post(
        TICKETS_URL,
        json=ticket_payload(
            ticket_context,
            assigned_to_user_id=other_analyst["id"],
        ),
        headers=ticket_context["headers"],
    )

    assert response.status_code == 409
    assert response.json()["error"] == "chamados_ticket_invalid_assigned_user"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", " "),
        ("description", " "),
        ("status", "invalid"),
        ("priority", "urgent"),
        ("client_id", "invalid"),
    ],
)
def test_create_ticket_rejects_invalid_data(
    client: TestClient,
    ticket_context: dict[str, object],
    field: str,
    value: object,
) -> None:
    """O contrato rejeita dados inválidos antes do serviço."""

    payload = ticket_payload(ticket_context)
    payload[field] = value

    response = client.post(
        TICKETS_URL,
        json=payload,
        headers=ticket_context["headers"],
    )

    assert response.status_code == 422


def test_unknown_ticket_returns_not_found(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """UUID inexistente retorna erro controlado."""

    ticket_id = str(uuid4())
    response = client.get(
        f"{TICKETS_URL}/{ticket_id}",
        headers=ticket_context["headers"],
    )

    assert response.status_code == 404
    assert response.json()["error"] == "chamados_ticket_not_found"


def test_ticket_id_requires_36_characters(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """A rota rejeita identificadores fora do tamanho de UUID."""

    response = client.get(
        f"{TICKETS_URL}/invalid",
        headers=ticket_context["headers"],
    )

    assert response.status_code == 422


def test_ticket_has_no_physical_delete_endpoint(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """Chamados são encerrados, nunca removidos fisicamente pela API."""

    ticket = create_ticket(client, ticket_context)

    response = client.delete(
        f"{TICKETS_URL}/{ticket['id']}",
        headers=ticket_context["headers"],
    )

    assert response.status_code == 405
