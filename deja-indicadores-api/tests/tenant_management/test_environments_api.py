from fastapi.testclient import TestClient

ORGANIZATIONS_URL = "/api/v1/organizations"
TENANTS_URL = "/api/v1/tenants"
ENVIRONMENTS_URL = "/api/v1/environments"


def create_organization(client: TestClient) -> dict[str, object]:
    """Cadastra a organização utilizada pelos testes."""

    response = client.post(
        ORGANIZATIONS_URL,
        json={
            "name": "Organização Principal",
            "status": "active",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_tenant(
    client: TestClient,
    organization_id: str,
    name: str = "Tenant Principal",
) -> dict[str, object]:
    """Cadastra o tenant utilizado pelos testes."""

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization_id,
            "name": name,
            "status": "active",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_environment(
    client: TestClient,
    tenant_id: str,
    name: str = "Produção",
    status: str = "active",
) -> dict[str, object]:
    """Cadastra um ambiente e retorna sua representação pública."""

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": tenant_id,
            "name": name,
            "status": status,
        },
    )

    assert response.status_code == 201
    return response.json()


def create_hierarchy(
    client: TestClient,
) -> tuple[dict[str, object], dict[str, object]]:
    """Cadastra uma organização e seu tenant."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )

    return organization, tenant


def test_create_environment(client: TestClient) -> None:
    """Cadastra um ambiente vinculado a um tenant existente."""

    _, tenant = create_hierarchy(client)

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": tenant["id"],
            "name": "  Produção  ",
            "status": "active",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["tenant_id"] == tenant["id"]
    assert body["name"] == "Produção"
    assert body["status"] == "active"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_environment_uses_default_status(
    client: TestClient,
) -> None:
    """Utiliza provisioning quando o status não é informado."""

    _, tenant = create_hierarchy(client)

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": tenant["id"],
            "name": "Homologação",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "provisioning"


def test_list_environments_ordered_by_name(
    client: TestClient,
) -> None:
    """Lista os ambientes ordenados alfabeticamente pelo nome."""

    _, tenant = create_hierarchy(client)

    create_environment(
        client,
        str(tenant["id"]),
        name="Produção",
    )
    create_environment(
        client,
        str(tenant["id"]),
        name="Desenvolvimento",
    )
    create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )

    response = client.get(ENVIRONMENTS_URL)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 3
    assert [environment["name"] for environment in body] == [
        "Desenvolvimento",
        "Homologação",
        "Produção",
    ]


def test_get_environment_by_id(client: TestClient) -> None:
    """Consulta um ambiente pelo identificador."""

    _, tenant = create_hierarchy(client)
    environment = create_environment(
        client,
        str(tenant["id"]),
    )

    response = client.get(
        f"{ENVIRONMENTS_URL}/{environment['id']}"
    )

    assert response.status_code == 200
    assert response.json() == environment


def test_update_environment(client: TestClient) -> None:
    """Atualiza integralmente um ambiente."""

    _, tenant = create_hierarchy(client)
    environment = create_environment(
        client,
        str(tenant["id"]),
    )

    response = client.put(
        f"{ENVIRONMENTS_URL}/{environment['id']}",
        json={
            "tenant_id": tenant["id"],
            "name": "  Homologação  ",
            "status": "inactive",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == environment["id"]
    assert body["tenant_id"] == tenant["id"]
    assert body["name"] == "Homologação"
    assert body["status"] == "inactive"
    assert body["created_at"] == environment["created_at"]
    assert body["updated_at"]


def test_move_environment_to_another_tenant(
    client: TestClient,
) -> None:
    """Permite transferir um ambiente para outro tenant."""

    organization, first_tenant = create_hierarchy(client)

    second_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Secundário",
    )

    environment = create_environment(
        client,
        str(first_tenant["id"]),
    )

    response = client.put(
        f"{ENVIRONMENTS_URL}/{environment['id']}",
        json={
            "tenant_id": second_tenant["id"],
            "name": environment["name"],
            "status": environment["status"],
        },
    )

    assert response.status_code == 200
    assert response.json()["tenant_id"] == second_tenant["id"]


def test_delete_environment(client: TestClient) -> None:
    """Exclui um ambiente existente."""

    _, tenant = create_hierarchy(client)
    environment = create_environment(
        client,
        str(tenant["id"]),
    )

    response = client.delete(
        f"{ENVIRONMENTS_URL}/{environment['id']}"
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        f"{ENVIRONMENTS_URL}/{environment['id']}"
    )

    assert get_response.status_code == 404
    assert get_response.json()["error"] == "environment_not_found"


def test_create_environment_requires_existing_tenant(
    client: TestClient,
) -> None:
    """Rejeita ambiente vinculado a um tenant inexistente."""

    tenant_id = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": tenant_id,
            "name": "Produção",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "tenant_not_found"


def test_create_environment_rejects_duplicate_name_in_tenant(
    client: TestClient,
) -> None:
    """Rejeita nomes duplicados dentro do mesmo tenant."""

    _, tenant = create_hierarchy(client)

    create_environment(
        client,
        str(tenant["id"]),
    )

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": tenant["id"],
            "name": "Produção",
            "status": "inactive",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == (
        "environment_name_already_exists"
    )


def test_same_environment_name_is_allowed_in_different_tenants(
    client: TestClient,
) -> None:
    """Permite nomes iguais quando pertencem a tenants diferentes."""

    organization, first_tenant = create_hierarchy(client)

    second_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Secundário",
    )

    create_environment(
        client,
        str(first_tenant["id"]),
    )

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": second_tenant["id"],
            "name": "Produção",
            "status": "active",
        },
    )

    assert response.status_code == 201


def test_update_environment_rejects_duplicate_name(
    client: TestClient,
) -> None:
    """Rejeita atualização para o nome de outro ambiente do tenant."""

    _, tenant = create_hierarchy(client)

    first_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Produção",
    )
    second_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )

    response = client.put(
        f"{ENVIRONMENTS_URL}/{second_environment['id']}",
        json={
            "tenant_id": tenant["id"],
            "name": first_environment["name"],
            "status": "active",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == (
        "environment_name_already_exists"
    )


def test_tenant_with_environment_cannot_be_deleted(
    client: TestClient,
) -> None:
    """Bloqueia a exclusão de tenant que possua ambientes."""

    _, tenant = create_hierarchy(client)

    create_environment(
        client,
        str(tenant["id"]),
    )

    response = client.delete(f"{TENANTS_URL}/{tenant['id']}")

    assert response.status_code == 409
    assert response.json()["error"] == "tenant_has_environments"


def test_get_unknown_environment_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao consultar um ambiente inexistente."""

    environment_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"{ENVIRONMENTS_URL}/{environment_id}"
    )

    assert response.status_code == 404
    assert response.json()["error"] == "environment_not_found"


def test_update_unknown_environment_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao atualizar um ambiente inexistente."""

    _, tenant = create_hierarchy(client)
    environment_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"{ENVIRONMENTS_URL}/{environment_id}",
        json={
            "tenant_id": tenant["id"],
            "name": "Ambiente Inexistente",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "environment_not_found"


def test_delete_unknown_environment_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao excluir um ambiente inexistente."""

    environment_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"{ENVIRONMENTS_URL}/{environment_id}"
    )

    assert response.status_code == 404
    assert response.json()["error"] == "environment_not_found"


def test_create_environment_rejects_blank_name(
    client: TestClient,
) -> None:
    """Rejeita nome composto exclusivamente por espaços."""

    _, tenant = create_hierarchy(client)

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": tenant["id"],
            "name": "   ",
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_create_environment_rejects_invalid_status(
    client: TestClient,
) -> None:
    """Rejeita um estado não previsto pelo Tenant Management."""

    _, tenant = create_hierarchy(client)

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": tenant["id"],
            "name": "Ambiente Inválido",
            "status": "unknown",
        },
    )

    assert response.status_code == 422