from uuid import uuid4

from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import create_user
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)
from tests.chamados.test_portal_api import (
    TICKETS_URL,
    create_portal_context,
)


def create_ticket_for_comments(
    client: TestClient,
    context: dict[str, object],
) -> dict[str, object]:
    """Cria um chamado para os testes administrativos de comentários."""

    administrator_headers = context["administrator_headers"]
    environment = context["environment"]
    chamados_client = context["client"]

    assert isinstance(administrator_headers, dict)
    assert isinstance(environment, dict)
    assert isinstance(chamados_client, dict)

    response = client.post(
        TICKETS_URL,
        headers=administrator_headers,
        json={
            "environment_id": str(environment["id"]),
            "client_id": str(chamados_client["id"]),
            "title": "Chamado para comentários",
            "description": "Validar comentários administrativos.",
            "priority": "medium",
            "assigned_to_user_id": None,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_operator_creates_public_ticket_comment(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Operador cria comentário público em chamado autorizado."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]
    administrator = context["administrator"]

    assert isinstance(administrator_headers, dict)
    assert isinstance(administrator, dict)

    ticket = create_ticket_for_comments(
        client,
        context,
    )

    response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/comments",
        headers=administrator_headers,
        json={
            "content": "  Comentário público da equipe.  ",
            "visibility": "public",
        },
    )

    assert response.status_code == 201

    comment = response.json()

    assert comment["ticket_id"] == ticket["id"]
    assert comment["content"] == "Comentário público da equipe."
    assert comment["visibility"] == "public"
    assert comment["created_by_user_id"] == administrator["id"]
    assert comment["created_by"] == administrator["name"]
    assert comment["created_at"] is not None


def test_operator_comment_registers_timeline_event(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Comentário administrativo registra evento na timeline."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]

    assert isinstance(administrator_headers, dict)

    ticket = create_ticket_for_comments(
        client,
        context,
    )

    create_response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/comments",
        headers=administrator_headers,
        json={
            "content": "Comentário registrado na timeline.",
            "visibility": "public",
        },
    )

    assert create_response.status_code == 201

    timeline_response = client.get(
        f"{TICKETS_URL}/{ticket['id']}/timeline",
        headers=administrator_headers,
    )

    assert timeline_response.status_code == 200

    timeline = timeline_response.json()

    assert any(
        event["event_type"] == "comment_added"
        and event["description"] == "Comentário adicionado."
        for event in timeline
    )

def test_operator_creates_internal_ticket_comment(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Operador cria comentário interno em chamado autorizado."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]
    administrator = context["administrator"]

    assert isinstance(administrator_headers, dict)
    assert isinstance(administrator, dict)

    ticket = create_ticket_for_comments(
        client,
        context,
    )

    response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/comments",
        headers=administrator_headers,
        json={
            "content": "Observação exclusiva da equipe.",
            "visibility": "internal",
        },
    )

    assert response.status_code == 201

    comment = response.json()

    assert comment["ticket_id"] == ticket["id"]
    assert comment["content"] == "Observação exclusiva da equipe."
    assert comment["visibility"] == "internal"
    assert comment["created_by_user_id"] == administrator["id"]
    assert comment["created_by"] == administrator["name"]
    assert comment["created_at"] is not None


def test_reader_lists_public_and_internal_ticket_comments(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Leitor administrativo consulta comentários públicos e internos."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]
    administrator = context["administrator"]
    organization = context["organization"]
    tenant = context["tenant"]
    environment = context["environment"]

    for value in (
        administrator_headers,
        administrator,
        organization,
        tenant,
        environment,
    ):
        assert isinstance(value, dict)

    ticket = create_ticket_for_comments(
        client,
        context,
    )

    for content, visibility in (
        ("Comentário público.", "public"),
        ("Comentário interno.", "internal"),
    ):
        create_response = client.post(
            f"{TICKETS_URL}/{ticket['id']}/comments",
            headers=administrator_headers,
            json={
                "content": content,
                "visibility": visibility,
            },
        )

        assert create_response.status_code == 201

    viewer = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"viewer-comments-{uuid4()}@deja.com",
        role="viewer",
    )

    viewer_headers = authorization_headers(
        test_settings,
        viewer,
    )

    response = client.get(
        f"{TICKETS_URL}/{ticket['id']}/comments",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    comments = response.json()

    assert len(comments) == 2

    comments_by_visibility = {
        comment["visibility"]: comment
        for comment in comments
    }

    public_comment = comments_by_visibility["public"]
    internal_comment = comments_by_visibility["internal"]

    assert public_comment["content"] == "Comentário público."
    assert public_comment["created_by_user_id"] == administrator["id"]
    assert public_comment["created_by"] == administrator["name"]

    assert internal_comment["content"] == "Comentário interno."
    assert internal_comment["created_by_user_id"] == administrator["id"]
    assert internal_comment["created_by"] == administrator["name"]


def test_viewer_cannot_create_ticket_comment(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Viewer pode consultar comentários, mas não pode criá-los."""

    context = create_portal_context(
        client,
        test_settings,
    )

    organization = context["organization"]
    tenant = context["tenant"]
    environment = context["environment"]

    for value in (
        organization,
        tenant,
        environment,
    ):
        assert isinstance(value, dict)

    ticket = create_ticket_for_comments(
        client,
        context,
    )

    viewer = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"viewer-create-comment-{uuid4()}@deja.com",
        role="viewer",
    )

    viewer_headers = authorization_headers(
        test_settings,
        viewer,
    )

    response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/comments",
        headers=viewer_headers,
        json={
            "content": "Viewer não pode adicionar comentário.",
            "visibility": "public",
        },
    )

    assert response.status_code == 403