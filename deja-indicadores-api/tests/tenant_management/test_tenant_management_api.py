from fastapi.testclient import TestClient


ORGANIZATIONS_URL = "/api/v1/organizations"

FIRST_ORGANIZATION = {
    "name": "  Organização Principal  ",
    "status": "active",
}

SECOND_ORGANIZATION = {
    "name": "Organização Secundária",
    "status": "inactive",
}


def create_organization(
    client: TestClient,
    payload: dict[str, str] | None = None,
) -> dict[str, object]:
    """Cadastra uma organização e retorna sua representação pública."""

    response = client.post(
        ORGANIZATIONS_URL,
        json=payload or FIRST_ORGANIZATION,
    )

    assert response.status_code == 201
    return response.json()


def test_create_organization(client: TestClient) -> None:
    """Cadastra uma organização normalizando seu nome."""

    response = client.post(
        ORGANIZATIONS_URL,
        json=FIRST_ORGANIZATION,
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["name"] == "Organização Principal"
    assert body["status"] == "active"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_organization_uses_default_status(
    client: TestClient,
) -> None:
    """Utiliza provisioning quando o status não é informado."""

    response = client.post(
        ORGANIZATIONS_URL,
        json={"name": "Nova Organização"},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "provisioning"


def test_list_organizations_ordered_by_name(
    client: TestClient,
) -> None:
    """Lista organizações ordenadas alfabeticamente pelo nome."""

    create_organization(client, SECOND_ORGANIZATION)
    create_organization(client, FIRST_ORGANIZATION)

    response = client.get(ORGANIZATIONS_URL)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert [organization["name"] for organization in body] == [
        "Organização Principal",
        "Organização Secundária",
    ]


def test_get_organization_by_id(client: TestClient) -> None:
    """Consulta uma organização pelo identificador."""

    organization = create_organization(client)

    response = client.get(
        f"{ORGANIZATIONS_URL}/{organization['id']}"
    )

    assert response.status_code == 200
    assert response.json() == organization


def test_update_organization(client: TestClient) -> None:
    """Atualiza integralmente uma organização."""

    organization = create_organization(client)

    response = client.put(
        f"{ORGANIZATIONS_URL}/{organization['id']}",
        json={
            "name": "  Organização Atualizada  ",
            "status": "inactive",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == organization["id"]
    assert body["name"] == "Organização Atualizada"
    assert body["status"] == "inactive"
    assert body["created_at"] == organization["created_at"]
    assert body["updated_at"]


def test_delete_organization(client: TestClient) -> None:
    """Exclui uma organização sem tenants cadastrados."""

    organization = create_organization(client)

    response = client.delete(
        f"{ORGANIZATIONS_URL}/{organization['id']}"
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        f"{ORGANIZATIONS_URL}/{organization['id']}"
    )

    assert get_response.status_code == 404
    assert get_response.json()["error"] == "organization_not_found"


def test_create_organization_rejects_duplicate_name(
    client: TestClient,
) -> None:
    """Rejeita o cadastro de organizações com nomes duplicados."""

    create_organization(client)

    response = client.post(
        ORGANIZATIONS_URL,
        json={
            "name": "Organização Principal",
            "status": "inactive",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == (
        "organization_name_already_exists"
    )


def test_update_organization_rejects_duplicate_name(
    client: TestClient,
) -> None:
    """Rejeita a atualização para o nome de outra organização."""

    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        SECOND_ORGANIZATION,
    )

    response = client.put(
        f"{ORGANIZATIONS_URL}/{second_organization['id']}",
        json={
            "name": first_organization["name"],
            "status": "active",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == (
        "organization_name_already_exists"
    )


def test_get_unknown_organization_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao consultar uma organização inexistente."""

    organization_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"{ORGANIZATIONS_URL}/{organization_id}"
    )

    assert response.status_code == 404
    assert response.json()["error"] == "organization_not_found"


def test_update_unknown_organization_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao atualizar uma organização inexistente."""

    organization_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"{ORGANIZATIONS_URL}/{organization_id}",
        json={
            "name": "Organização Inexistente",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "organization_not_found"


def test_delete_unknown_organization_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao excluir uma organização inexistente."""

    organization_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"{ORGANIZATIONS_URL}/{organization_id}"
    )

    assert response.status_code == 404
    assert response.json()["error"] == "organization_not_found"


def test_create_organization_rejects_blank_name(
    client: TestClient,
) -> None:
    """Rejeita nome composto exclusivamente por espaços."""

    response = client.post(
        ORGANIZATIONS_URL,
        json={
            "name": "   ",
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_create_organization_rejects_invalid_status(
    client: TestClient,
) -> None:
    """Rejeita um estado não previsto pelo Tenant Management."""

    response = client.post(
        ORGANIZATIONS_URL,
        json={
            "name": "Organização Inválida",
            "status": "unknown",
        },
    )

    assert response.status_code == 422


def test_organization_id_requires_36_characters(
    client: TestClient,
) -> None:
    """Rejeita identificador que não possui 36 caracteres."""

    response = client.get(
        f"{ORGANIZATIONS_URL}/invalid-id"
    )

    assert response.status_code == 422