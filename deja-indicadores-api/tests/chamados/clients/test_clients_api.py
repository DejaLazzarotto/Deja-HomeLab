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
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)

CLIENTS_URL = "/api/chamados/clients"

FIRST_CLIENT = {
    "company_name": "Deja Tecnologia Ltda",
    "fantasy_name": "Deja Tecnologia",
    "document": "12.345.678/0001-90",
    "contact_name": "Maria da Silva",
    "phone": " (54) 3222-3344 ",
    "whatsapp": " (54) 99988-7766 ",
    "email": " CONTATO@DEJA.COM.BR ",
    "city": " Caxias do Sul ",
    "state": " rs ",
    "notes": " Cliente prioritário. ",
    "active": True,
}

SECOND_CLIENT = {
    "company_name": "Empresa Exemplo Ltda",
    "fantasy_name": "Empresa Exemplo",
    "document": "98.765.432/0001-10",
    "contact_name": "João da Silva",
    "phone": "5432224455",
    "whatsapp": "54999776655",
    "email": "contato@exemplo.com.br",
    "city": "Farroupilha",
    "state": "RS",
    "notes": "",
    "active": False,
}


@pytest.fixture()
def client_context(
    client: TestClient,
    test_settings: Settings,
) -> tuple[str, str, str, Mapping[str, str]]:
    """Cria a hierarquia e a identidade global para os testes."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    administrator = create_user(
        client,
        None,
        email="platform.admin.chamados.clients@deja.com",
        role="platform_admin",
    )

    return (
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
        authorization_headers(test_settings, administrator),
    )


def client_payload(
    payload: dict[str, object],
    environment_id: str,
) -> dict[str, object]:
    """Adiciona o ambiente institucional ao contrato do cliente."""

    return {
        "environment_id": environment_id,
        **payload,
    }


def create_client(
    client: TestClient,
    payload: dict[str, object],
    environment_id: str,
    headers: Mapping[str, str],
) -> dict[str, object]:
    """Cadastra um cliente e retorna o corpo da resposta."""

    response = client.post(
        CLIENTS_URL,
        json=client_payload(payload, environment_id),
        headers=headers,
    )

    assert response.status_code == 201
    return response.json()


def test_create_client_normalizes_and_derives_scope(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Cadastra um cliente e deriva organização e tenant do ambiente."""

    (
        organization_id,
        tenant_id,
        environment_id,
        headers,
    ) = client_context
    payload = {
        **FIRST_CLIENT,
        "company_name": "  Deja Tecnologia Ltda  ",
        "fantasy_name": "  Deja Tecnologia  ",
        "contact_name": "  Maria da Silva  ",
    }

    response = client.post(
        CLIENTS_URL,
        json=client_payload(payload, environment_id),
        headers=headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["organization_id"] == organization_id
    assert body["tenant_id"] == tenant_id
    assert body["environment_id"] == environment_id
    assert body["company_name"] == "Deja Tecnologia Ltda"
    assert body["fantasy_name"] == "Deja Tecnologia"
    assert body["document"] == "12345678000190"
    assert body["contact_name"] == "Maria da Silva"
    assert body["phone"] == "5432223344"
    assert body["whatsapp"] == "54999887766"
    assert body["email"] == "contato@deja.com.br"
    assert body["city"] == "Caxias do Sul"
    assert body["state"] == "RS"
    assert body["notes"] == "Cliente prioritário."
    assert body["active"] is True
    assert body["total_tickets"] == 0
    assert body["created_at"]
    assert body["updated_at"]


def test_list_clients_filters_by_search_and_active(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Lista clientes aplicando busca textual e situação."""

    _, _, environment_id, headers = client_context
    create_client(
        client,
        FIRST_CLIENT,
        environment_id,
        headers,
    )
    second_client = create_client(
        client,
        SECOND_CLIENT,
        environment_id,
        headers,
    )

    response = client.get(
        CLIENTS_URL,
        params={
            "search": "Exemplo",
            "active": "false",
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert [returned_client["id"] for returned_client in response.json()] == [second_client["id"]]


def test_list_clients_returns_fantasy_name_order(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Lista os clientes ordenados pelo nome fantasia."""

    _, _, environment_id, headers = client_context
    create_client(
        client,
        SECOND_CLIENT,
        environment_id,
        headers,
    )
    create_client(
        client,
        FIRST_CLIENT,
        environment_id,
        headers,
    )

    response = client.get(
        CLIENTS_URL,
        headers=headers,
    )

    assert response.status_code == 200
    assert [returned_client["fantasy_name"] for returned_client in response.json()] == [
        "Deja Tecnologia",
        "Empresa Exemplo",
    ]


def test_get_client_by_id(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Consulta um cliente pelo identificador."""

    _, _, environment_id, headers = client_context
    created_client = create_client(
        client,
        FIRST_CLIENT,
        environment_id,
        headers,
    )

    response = client.get(
        f"{CLIENTS_URL}/{created_client['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == created_client


def test_update_client(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Atualiza integralmente um cliente existente."""

    _, _, environment_id, headers = client_context
    created_client = create_client(
        client,
        FIRST_CLIENT,
        environment_id,
        headers,
    )
    update_payload = {
        **FIRST_CLIENT,
        "company_name": "Deja Sistemas Ltda",
        "fantasy_name": "Deja Sistemas",
        "contact_name": "Ana da Silva",
        "email": "sistemas@deja.com.br",
        "active": False,
    }

    response = client.put(
        f"{CLIENTS_URL}/{created_client['id']}",
        json=client_payload(
            update_payload,
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == created_client["id"]
    assert body["environment_id"] == environment_id
    assert body["company_name"] == "Deja Sistemas Ltda"
    assert body["fantasy_name"] == "Deja Sistemas"
    assert body["contact_name"] == "Ana da Silva"
    assert body["email"] == "sistemas@deja.com.br"
    assert body["active"] is False
    assert body["document"] == "12345678000190"


def test_delete_client(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Exclui um cliente e impede consultas posteriores."""

    _, _, environment_id, headers = client_context
    created_client = create_client(
        client,
        FIRST_CLIENT,
        environment_id,
        headers,
    )

    delete_response = client.delete(
        f"{CLIENTS_URL}/{created_client['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"{CLIENTS_URL}/{created_client['id']}",
        headers=headers,
    )

    assert get_response.status_code == 404
    assert get_response.json()["error"] == "chamados_client_not_found"


def test_create_client_rejects_duplicate_document_in_organization(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita documento repetido dentro da mesma organização."""

    _, _, environment_id, headers = client_context
    create_client(
        client,
        FIRST_CLIENT,
        environment_id,
        headers,
    )

    response = client.post(
        CLIENTS_URL,
        json=client_payload(
            {
                **SECOND_CLIENT,
                "document": FIRST_CLIENT["document"],
            },
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"] == ("chamados_client_document_already_exists")


def test_same_document_is_allowed_in_different_organizations(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Mantém a unicidade do documento restrita à organização."""

    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )
    first_tenant = create_tenant(
        client,
        str(first_organization["id"]),
    )
    second_tenant = create_tenant(
        client,
        str(second_organization["id"]),
    )
    first_environment = create_environment(
        client,
        str(first_tenant["id"]),
    )
    second_environment = create_environment(
        client,
        str(second_tenant["id"]),
    )
    administrator = create_user(
        client,
        None,
        email="platform.admin.documents@deja.com",
        role="platform_admin",
    )
    headers = authorization_headers(
        test_settings,
        administrator,
    )

    first_response = client.post(
        CLIENTS_URL,
        json=client_payload(
            FIRST_CLIENT,
            str(first_environment["id"]),
        ),
        headers=headers,
    )
    second_response = client.post(
        CLIENTS_URL,
        json=client_payload(
            FIRST_CLIENT,
            str(second_environment["id"]),
        ),
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["organization_id"] != second_response.json()["organization_id"]


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("document", "1234"),
        ("phone", "123"),
        ("whatsapp", "123"),
        ("email", "email-invalido"),
        ("state", "RIO"),
    ],
)
def test_create_client_rejects_invalid_data(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
    field_name: str,
    invalid_value: str,
) -> None:
    """Rejeita dados comerciais inválidos."""

    _, _, environment_id, headers = client_context
    response = client.post(
        CLIENTS_URL,
        json=client_payload(
            {
                **FIRST_CLIENT,
                field_name: invalid_value,
            },
            environment_id,
        ),
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "method",
    [
        "get",
        "put",
        "delete",
    ],
)
def test_unknown_client_returns_not_found(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
    method: str,
) -> None:
    """Retorna 404 nas operações sobre cliente inexistente."""

    _, _, environment_id, headers = client_context
    client_id = str(uuid4())
    request = getattr(client, method)
    request_arguments: dict[str, object] = {
        "headers": headers,
    }

    if method == "put":
        request_arguments["json"] = client_payload(
            FIRST_CLIENT,
            environment_id,
        )

    response = request(
        f"{CLIENTS_URL}/{client_id}",
        **request_arguments,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "chamados_client_not_found"


def test_client_id_requires_36_characters(
    client: TestClient,
    client_context: tuple[
        str,
        str,
        str,
        Mapping[str, str],
    ],
) -> None:
    """Rejeita identificador que não possui 36 caracteres."""

    _, _, _, headers = client_context
    response = client.get(
        f"{CLIENTS_URL}/invalid-id",
        headers=headers,
    )

    assert response.status_code == 422
