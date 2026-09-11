from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_user_authorization_api import authorization_headers
from tests.chamados.tickets.test_tickets_api import (
    TICKETS_URL,
    create_ticket,
)

pytest_plugins = (
    "tests.chamados.tickets.test_tickets_api",
)

TIMELINE_SUFFIX = "/timeline"


def test_ticket_creation_registers_timeline_event(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """A abertura do chamado registra o evento inicial."""

    ticket = create_ticket(client, ticket_context)

    response = client.get(
        f"{TICKETS_URL}/{ticket['id']}{TIMELINE_SUFFIX}",
        headers=ticket_context["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1

    event = body[0]
    assert len(event["id"]) == 36
    assert event["ticket_id"] == ticket["id"]
    assert event["event_type"] == "created"
    assert event["description"] == "Chamado criado."
    assert event["previous_value"] is None
    assert event["new_value"] == "created"
    assert event["previous_display_value"] is None
    assert event["new_display_value"] is None
    assert event["created_by_user_id"] == ticket_context["administrator"]["id"]
    assert event["created_at"] is not None


def test_ticket_update_registers_changed_fields(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """Prioridade, responsável e conteúdo alterados entram no histórico."""

    ticket = create_ticket(client, ticket_context)
    analyst = ticket_context["analyst"]
    assert isinstance(analyst, dict)

    update_response = client.put(
        f"{TICKETS_URL}/{ticket['id']}",
        json={
            "title": "Novo título",
            "description": "Nova descrição",
            "priority": "critical",
            "assigned_to_user_id": analyst["id"],
        },
        headers=ticket_context["headers"],
    )

    assert update_response.status_code == 200

    response = client.get(
        f"{TICKETS_URL}/{ticket['id']}{TIMELINE_SUFFIX}",
        headers=ticket_context["headers"],
    )

    assert response.status_code == 200
    body = response.json()

    assert [event["event_type"] for event in body] == [
        "created",
        "priority_changed",
        "assigned_changed",
        "updated",
    ]

    priority_event = body[1]
    assert priority_event["previous_value"] == "high"
    assert priority_event["new_value"] == "critical"
    assert priority_event["previous_display_value"] is None
    assert priority_event["new_display_value"] is None

    assigned_event = body[2]
    assert assigned_event["previous_value"] is None
    assert assigned_event["new_value"] == analyst["id"]
    assert assigned_event["previous_display_value"] is None
    assert assigned_event["new_display_value"] == analyst["name"]


def test_status_change_and_reopen_register_timeline(
    client: TestClient,
    ticket_context: dict[str, object],
) -> None:
    """Encerramento e reabertura preservam as transições de status."""

    ticket = create_ticket(client, ticket_context)

    close_response = client.patch(
        f"{TICKETS_URL}/{ticket['id']}/status",
        json={"status": "closed"},
        headers=ticket_context["headers"],
    )
    assert close_response.status_code == 200

    reopen_response = client.patch(
        f"{TICKETS_URL}/{ticket['id']}/status",
        json={"status": "open"},
        headers=ticket_context["headers"],
    )
    assert reopen_response.status_code == 200

    response = client.get(
        f"{TICKETS_URL}/{ticket['id']}{TIMELINE_SUFFIX}",
        headers=ticket_context["headers"],
    )

    assert response.status_code == 200
    body = response.json()

    status_events = [
        event
        for event in body
        if event["event_type"] == "status_changed"
    ]

    assert len(status_events) == 2
    assert status_events[0]["previous_value"] == "open"
    assert status_events[0]["new_value"] == "closed"
    assert status_events[0]["previous_display_value"] is None
    assert status_events[0]["new_display_value"] is None
    assert status_events[1]["previous_value"] == "closed"
    assert status_events[1]["new_value"] == "open"
    assert status_events[1]["previous_display_value"] is None
    assert status_events[1]["new_display_value"] is None


def test_viewer_can_read_timeline(
    client: TestClient,
    ticket_context: dict[str, object],
    test_settings: Settings,
) -> None:
    """Viewer pode consultar o histórico dentro do próprio escopo."""

    ticket = create_ticket(client, ticket_context)
    organization = ticket_context["organization"]
    tenant = ticket_context["tenant"]
    environment = ticket_context["environment"]

    for value in (organization, tenant, environment):
        assert isinstance(value, dict)

    from tests.authentication.test_authentication_api import create_user

    viewer = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="viewer.timeline@deja.com",
        role="viewer",
    )
    headers = authorization_headers(test_settings, viewer)

    response = client.get(
        f"{TICKETS_URL}/{ticket['id']}{TIMELINE_SUFFIX}",
        headers=headers,
    )

    assert response.status_code == 200

    event = response.json()[0]
    assert event["event_type"] == "created"
    assert event["previous_display_value"] is None
    assert event["new_display_value"] is None