from pathlib import Path
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


def create_ticket_for_attachments(
    client: TestClient,
    context: dict[str, object],
) -> dict[str, object]:
    """Cria um chamado para os testes administrativos de anexos."""

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
            "title": "Chamado para anexos",
            "description": "Validar anexos administrativos.",
            "priority": "medium",
            "assigned_to_user_id": None,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_operator_uploads_ticket_attachment(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Operador adiciona um anexo em chamado autorizado."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]
    administrator = context["administrator"]

    assert isinstance(administrator_headers, dict)
    assert isinstance(administrator, dict)

    ticket = create_ticket_for_attachments(
        client,
        context,
    )

    response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=administrator_headers,
        files={
            "file": (
                "comprovante.pdf",
                b"%PDF-1.4 teste de anexo",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    attachment = response.json()

    assert attachment["ticket_id"] == ticket["id"]
    assert attachment["original_name"] == "comprovante.pdf"
    assert attachment["content_type"] == "application/pdf"
    assert attachment["file_size"] == len(
        b"%PDF-1.4 teste de anexo"
    )
    assert attachment["created_by_user_id"] == administrator["id"]
    assert attachment["created_by"] == administrator["name"]
    assert attachment["created_at"] is not None
    assert "file_path" not in attachment
    assert "file_name" not in attachment

    stored_files = list(
        (
            test_settings.uploads_dir
            / "chamados"
            / "tickets"
            / str(ticket["id"])
        ).iterdir()
    )

    assert len(stored_files) == 1
    assert stored_files[0].suffix == ".pdf"


def test_reader_lists_ticket_attachments(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Leitor administrativo consulta anexos de chamado autorizado."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]
    organization = context["organization"]
    tenant = context["tenant"]
    environment = context["environment"]

    for value in (
        administrator_headers,
        organization,
        tenant,
        environment,
    ):
        assert isinstance(value, dict)

    ticket = create_ticket_for_attachments(
        client,
        context,
    )

    upload_response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=administrator_headers,
        files={
            "file": (
                "imagem.png",
                b"\x89PNG\r\n\x1a\narquivo de teste",
                "image/png",
            )
        },
    )

    assert upload_response.status_code == 201

    viewer = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"viewer-attachments-{uuid4()}@deja.com",
        role="viewer",
    )

    viewer_headers = authorization_headers(
        test_settings,
        viewer,
    )

    response = client.get(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=viewer_headers,
    )

    assert response.status_code == 200

    attachments = response.json()

    assert len(attachments) == 1
    assert attachments[0]["original_name"] == "imagem.png"
    assert attachments[0]["content_type"] == "image/png"


def test_viewer_cannot_upload_ticket_attachment(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Viewer pode consultar anexos, mas não pode enviá-los."""

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

    ticket = create_ticket_for_attachments(
        client,
        context,
    )

    viewer = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"viewer-upload-attachment-{uuid4()}@deja.com",
        role="viewer",
    )

    viewer_headers = authorization_headers(
        test_settings,
        viewer,
    )

    response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=viewer_headers,
        files={
            "file": (
                "arquivo.pdf",
                b"%PDF-1.4",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 403


def test_rejects_invalid_attachment_content_type(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Upload rejeita tipo de arquivo não permitido."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]

    assert isinstance(administrator_headers, dict)

    ticket = create_ticket_for_attachments(
        client,
        context,
    )

    response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=administrator_headers,
        files={
            "file": (
                "arquivo.txt",
                b"conteudo",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == (
        "chamados_ticket_attachment_invalid_type"
    )


def test_rejects_attachment_larger_than_configured_limit(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Upload rejeita arquivo acima do tamanho máximo configurado."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]

    assert isinstance(administrator_headers, dict)

    ticket = create_ticket_for_attachments(
        client,
        context,
    )

    original_limit = test_settings.ticket_attachment_max_size_mb
    test_settings.ticket_attachment_max_size_mb = 1

    try:
        response = client.post(
            f"{TICKETS_URL}/{ticket['id']}/attachments",
            headers=administrator_headers,
            files={
                "file": (
                    "grande.pdf",
                    b"x" * (1024 * 1024 + 1),
                    "application/pdf",
                )
            },
        )
    finally:
        test_settings.ticket_attachment_max_size_mb = original_limit

    assert response.status_code == 400
    assert response.json()["error"] == (
        "chamados_ticket_attachment_too_large"
    )


def test_reader_downloads_ticket_attachment(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Leitor autorizado baixa o arquivo original do anexo."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]

    assert isinstance(administrator_headers, dict)

    ticket = create_ticket_for_attachments(
        client,
        context,
    )

    file_content = b"%PDF-1.4 download teste"

    upload_response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=administrator_headers,
        files={
            "file": (
                "manual.pdf",
                file_content,
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 201

    attachment = upload_response.json()

    response = client.get(
        (
            f"{TICKETS_URL}/attachments/"
            f"{attachment['id']}/download"
        ),
        headers=administrator_headers,
    )

    assert response.status_code == 200
    assert response.content == file_content
    assert response.headers["content-type"] == "application/pdf"
    assert "manual.pdf" in response.headers["content-disposition"]


def test_operator_deletes_ticket_attachment(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Operador remove registro e arquivo físico do anexo."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]

    assert isinstance(administrator_headers, dict)

    ticket = create_ticket_for_attachments(
        client,
        context,
    )

    upload_response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=administrator_headers,
        files={
            "file": (
                "remover.webp",
                b"arquivo-webp",
                "image/webp",
            )
        },
    )

    assert upload_response.status_code == 201

    attachment = upload_response.json()

    ticket_upload_dir = (
        test_settings.uploads_dir
        / "chamados"
        / "tickets"
        / str(ticket["id"])
    )

    stored_files = list(ticket_upload_dir.iterdir())

    assert len(stored_files) == 1

    response = client.delete(
        f"{TICKETS_URL}/attachments/{attachment['id']}",
        headers=administrator_headers,
    )

    assert response.status_code == 204

    list_response = client.get(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=administrator_headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == []
    assert not stored_files[0].exists()


def test_download_missing_attachment_returns_not_found(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Download de anexo inexistente retorna 404."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]

    assert isinstance(administrator_headers, dict)

    response = client.get(
        f"{TICKETS_URL}/attachments/{uuid4()}/download",
        headers=administrator_headers,
    )

    assert response.status_code == 404


def test_upload_sanitizes_original_file_name(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Upload remove componentes de caminho do nome informado."""

    context = create_portal_context(
        client,
        test_settings,
    )

    administrator_headers = context["administrator_headers"]

    assert isinstance(administrator_headers, dict)

    ticket = create_ticket_for_attachments(
        client,
        context,
    )

    response = client.post(
        f"{TICKETS_URL}/{ticket['id']}/attachments",
        headers=administrator_headers,
        files={
            "file": (
                "../../arquivo.pdf",
                b"%PDF-1.4",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    attachment = response.json()

    assert Path(attachment["original_name"]).name == "arquivo.pdf"
    assert attachment["original_name"] == "arquivo.pdf"