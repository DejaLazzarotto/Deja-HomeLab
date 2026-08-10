from fastapi.testclient import TestClient


ORGANIZATIONS_URL = "/api/v1/organizations"
TENANTS_URL = "/api/v1/tenants"

ORGANIZATION_PAYLOAD = {
    "name": "Organização Principal",
    "status": "active",
}

TENANT_PAYLOAD = {
    "name": "  Tenant Principal  ",
    "status": "active",
}


def create_organization(client: TestClient) -> dict[str, object]:
    """Cadastra a organização utilizada pelos testes."""

    response = client.post(
        ORGANIZATIONS_URL,
        json=ORGANIZATION_PAYLOAD,
    )

    assert response.status_code == 201
    return response.json()


def create_tenant(
    client: TestClient,
    organization_id: str,
    name: str = "Tenant Principal",
    status: str = "active",
) -> dict[str, object]:
    """Cadastra um tenant e retorna sua representação pública."""

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization_id,
            "name": name,
            "status": status,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_tenant(client: TestClient) -> None:
    """Cadastra um tenant vinculado a uma organização existente."""

    organization = create_organization(client)

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization["id"],
            **TENANT_PAYLOAD,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["organization_id"] == organization["id"]
    assert body["name"] == "Tenant Principal"
    assert body["status"] == "active"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_tenant_uses_default_status(
    client: TestClient,
) -> None:
    """Utiliza provisioning quando o status não é informado."""

    organization = create_organization(client)

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization["id"],
            "name": "Novo Tenant",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "provisioning"


def test_list_tenants_ordered_by_name(
    client: TestClient,
) -> None:
    """Lista os tenants ordenados alfabeticamente pelo nome."""

    organization = create_organization(client)

    create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Secundário",
    )
    create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Principal",
    )

    response = client.get(TENANTS_URL)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert [tenant["name"] for tenant in body] == [
        "Tenant Principal",
        "Tenant Secundário",
    ]


def test_get_tenant_by_id(client: TestClient) -> None:
    """Consulta um tenant pelo identificador."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )

    response = client.get(f"{TENANTS_URL}/{tenant['id']}")

    assert response.status_code == 200
    assert response.json() == tenant


def test_update_tenant(client: TestClient) -> None:
    """Atualiza integralmente um tenant."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )

    response = client.put(
        f"{TENANTS_URL}/{tenant['id']}",
        json={
            "organization_id": organization["id"],
            "name": "  Tenant Atualizado  ",
            "status": "inactive",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == tenant["id"]
    assert body["organization_id"] == organization["id"]
    assert body["name"] == "Tenant Atualizado"
    assert body["status"] == "inactive"
    assert body["created_at"] == tenant["created_at"]
    assert body["updated_at"]


def test_move_tenant_to_another_organization(
    client: TestClient,
) -> None:
    """Permite transferir um tenant para outra organização."""

    first_organization = create_organization(client)

    second_response = client.post(
        ORGANIZATIONS_URL,
        json={
            "name": "Organização Secundária",
            "status": "active",
        },
    )

    assert second_response.status_code == 201
    second_organization = second_response.json()

    tenant = create_tenant(
        client,
        str(first_organization["id"]),
    )

    response = client.put(
        f"{TENANTS_URL}/{tenant['id']}",
        json={
            "organization_id": second_organization["id"],
            "name": tenant["name"],
            "status": tenant["status"],
        },
    )

    assert response.status_code == 200
    assert response.json()["organization_id"] == second_organization["id"]


def test_delete_tenant(client: TestClient) -> None:
    """Exclui um tenant sem ambientes cadastrados."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )

    response = client.delete(f"{TENANTS_URL}/{tenant['id']}")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"{TENANTS_URL}/{tenant['id']}")

    assert get_response.status_code == 404
    assert get_response.json()["error"] == "tenant_not_found"


def test_create_tenant_requires_existing_organization(
    client: TestClient,
) -> None:
    """Rejeita tenant vinculado a uma organização inexistente."""

    organization_id = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization_id,
            "name": "Tenant Órfão",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "organization_not_found"


def test_create_tenant_rejects_duplicate_name_in_organization(
    client: TestClient,
) -> None:
    """Rejeita nomes duplicados dentro da mesma organização."""

    organization = create_organization(client)

    create_tenant(
        client,
        str(organization["id"]),
    )

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization["id"],
            "name": "Tenant Principal",
            "status": "inactive",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == "tenant_name_already_exists"


def test_same_tenant_name_is_allowed_in_different_organizations(
    client: TestClient,
) -> None:
    """Permite nomes iguais quando pertencem a organizações diferentes."""

    first_organization = create_organization(client)

    second_response = client.post(
        ORGANIZATIONS_URL,
        json={
            "name": "Organização Secundária",
            "status": "active",
        },
    )

    assert second_response.status_code == 201
    second_organization = second_response.json()

    create_tenant(
        client,
        str(first_organization["id"]),
    )

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": second_organization["id"],
            "name": "Tenant Principal",
            "status": "active",
        },
    )

    assert response.status_code == 201


def test_update_tenant_rejects_duplicate_name(
    client: TestClient,
) -> None:
    """Rejeita atualização para o nome de outro tenant da organização."""

    organization = create_organization(client)

    first_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Principal",
    )
    second_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Secundário",
    )

    response = client.put(
        f"{TENANTS_URL}/{second_tenant['id']}",
        json={
            "organization_id": organization["id"],
            "name": first_tenant["name"],
            "status": "active",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == "tenant_name_already_exists"


def test_organization_with_tenant_cannot_be_deleted(
    client: TestClient,
) -> None:
    """Bloqueia a exclusão de organização que possua tenants."""

    organization = create_organization(client)

    create_tenant(
        client,
        str(organization["id"]),
    )

    response = client.delete(
        f"{ORGANIZATIONS_URL}/{organization['id']}"
    )

    assert response.status_code == 409
    assert response.json()["error"] == "organization_has_tenants"


def test_get_unknown_tenant_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao consultar um tenant inexistente."""

    tenant_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(f"{TENANTS_URL}/{tenant_id}")

    assert response.status_code == 404
    assert response.json()["error"] == "tenant_not_found"


def test_update_unknown_tenant_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao atualizar um tenant inexistente."""

    organization = create_organization(client)
    tenant_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"{TENANTS_URL}/{tenant_id}",
        json={
            "organization_id": organization["id"],
            "name": "Tenant Inexistente",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "tenant_not_found"


def test_delete_unknown_tenant_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao excluir um tenant inexistente."""

    tenant_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(f"{TENANTS_URL}/{tenant_id}")

    assert response.status_code == 404
    assert response.json()["error"] == "tenant_not_found"


def test_create_tenant_rejects_blank_name(
    client: TestClient,
) -> None:
    """Rejeita nome composto exclusivamente por espaços."""

    organization = create_organization(client)

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization["id"],
            "name": "   ",
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_create_tenant_rejects_invalid_status(
    client: TestClient,
) -> None:
    """Rejeita um estado não previsto pelo Tenant Management."""

    organization = create_organization(client)

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization["id"],
            "name": "Tenant Inválido",
            "status": "unknown",
        },
    )

    assert response.status_code == 422