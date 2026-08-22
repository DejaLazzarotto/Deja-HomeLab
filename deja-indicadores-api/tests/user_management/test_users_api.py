from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.core.security import PasswordService
from deja_indicadores_api.user_management.models import UserModel

ORGANIZATIONS_URL = "/api/v1/organizations"
TENANTS_URL = "/api/v1/tenants"
ENVIRONMENTS_URL = "/api/v1/environments"
USERS_URL = "/api/v1/users"


def create_organization(
    client: TestClient,
    name: str = "Organização Principal",
) -> dict[str, object]:
    """Cadastra uma organização para os testes."""

    client.app.state.set_platform_test_administrator()

    response = client.post(
        ORGANIZATIONS_URL,
        json={
            "code": f"ORG-{uuid4().hex[:12].upper()}",
            "name": name,
            "status": "active",
        },
    )

    assert response.status_code == 201, response.text

    organization = response.json()
    client.app.state.set_current_test_organization(str(organization["id"]))

    return organization


def create_tenant(
    client: TestClient,
    organization_id: str,
    name: str = "Tenant Principal",
) -> dict[str, object]:
    """Cadastra um tenant para os testes."""

    client.app.state.set_current_test_organization(organization_id)

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
) -> dict[str, object]:
    """Cadastra um ambiente para os testes."""

    response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": tenant_id,
            "name": name,
            "status": "active",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_hierarchy(
    client: TestClient,
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    """Cadastra organização, tenant e ambiente relacionados."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )

    return organization, tenant, environment


def create_user(
    client: TestClient,
    organization_id: str,
    tenant_id: str | None = None,
    environment_id: str | None = None,
    name: str = "Usuário Principal",
    email: str = "usuario@deja.com",
    role: str = "viewer",
    status: str = "active",
) -> dict[str, object]:
    """Cadastra um usuário e retorna sua representação pública."""

    client.app.state.set_current_test_organization(organization_id)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization_id,
            "tenant_id": tenant_id,
            "environment_id": environment_id,
            "name": name,
            "email": email,
            "role": role,
            "status": status,
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


def test_create_organization_admin(client: TestClient) -> None:
    """Cadastra administrador no escopo da organização."""

    organization = create_organization(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "  Administrador Geral  ",
            "email": "  ADMIN@deja.com  ",
            "role": "organization_admin",
            "status": "active",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 36
    assert body["organization_id"] == organization["id"]
    assert body["tenant_id"] is None
    assert body["environment_id"] is None
    assert body["name"] == "Administrador Geral"
    assert body["email"] == "admin@deja.com"
    assert body["role"] == "organization_admin"
    assert body["status"] == "active"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_tenant_admin(client: TestClient) -> None:
    """Cadastra administrador no escopo de um tenant."""

    organization, tenant, _ = create_hierarchy(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": None,
            "name": "Administrador do Tenant",
            "email": "tenant.admin@deja.com",
            "role": "tenant_admin",
            "status": "active",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["organization_id"] == organization["id"]
    assert body["tenant_id"] == tenant["id"]
    assert body["environment_id"] is None
    assert body["role"] == "tenant_admin"


def test_create_user_with_environment(client: TestClient) -> None:
    """Cadastra usuário vinculado a tenant e ambiente."""

    organization, tenant, environment = create_hierarchy(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": "Analista Principal",
            "email": "analista@deja.com",
            "role": "analyst",
            "status": "active",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["organization_id"] == organization["id"]
    assert body["tenant_id"] == tenant["id"]
    assert body["environment_id"] == environment["id"]
    assert body["role"] == "analyst"


def test_create_user_uses_default_status(
    client: TestClient,
) -> None:
    """Utiliza active quando o status não é informado."""

    organization, tenant, environment = create_hierarchy(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": "Gestor Principal",
            "email": "gestor@deja.com",
            "role": "manager",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "active"


def test_list_users_ordered_by_name(
    client: TestClient,
) -> None:
    """Lista usuários ordenados pelo nome."""

    organization, tenant, environment = create_hierarchy(client)

    create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Secundário",
        email="secundario@deja.com",
    )
    create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Principal",
        email="principal@deja.com",
    )

    response = client.get(USERS_URL)

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert [user["name"] for user in body] == [
        "Usuário Principal",
        "Usuário Secundário",
    ]


def test_list_users_with_same_name_ordered_by_email(
    client: TestClient,
) -> None:
    """Ordena pelo e-mail quando usuários possuem o mesmo nome."""

    organization, tenant, environment = create_hierarchy(client)

    create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Compartilhado",
        email="segundo@deja.com",
    )
    create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Compartilhado",
        email="primeiro@deja.com",
    )

    response = client.get(USERS_URL)

    assert response.status_code == 200

    body = response.json()

    assert [user["email"] for user in body] == [
        "primeiro@deja.com",
        "segundo@deja.com",
    ]


def test_list_users_filtered_by_organization(
    client: TestClient,
) -> None:
    """Filtra usuários por organização."""

    first_organization = create_organization(client)

    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )

    create_user(
        client,
        str(first_organization["id"]),
        name="Administrador Principal",
        email="principal@deja.com",
        role="organization_admin",
    )
    expected_user = create_user(
        client,
        str(second_organization["id"]),
        name="Administrador Secundário",
        email="secundario@deja.com",
        role="organization_admin",
    )

    response = client.get(
        USERS_URL,
        params={
            "organization_id": second_organization["id"],
        },
    )

    assert response.status_code == 200
    assert response.json() == [expected_user]


def test_list_users_filtered_by_tenant(
    client: TestClient,
) -> None:
    """Filtra usuários por tenant."""

    organization = create_organization(client)

    first_tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    second_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Secundário",
    )

    first_environment = create_environment(
        client,
        str(first_tenant["id"]),
    )
    second_environment = create_environment(
        client,
        str(second_tenant["id"]),
        name="Homologação",
    )

    create_user(
        client,
        str(organization["id"]),
        tenant_id=str(first_tenant["id"]),
        environment_id=str(first_environment["id"]),
        name="Usuário Principal",
        email="principal@deja.com",
    )
    expected_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(second_tenant["id"]),
        environment_id=str(second_environment["id"]),
        name="Usuário Secundário",
        email="secundario@deja.com",
    )

    response = client.get(
        USERS_URL,
        params={
            "tenant_id": second_tenant["id"],
        },
    )

    assert response.status_code == 200
    assert response.json() == [expected_user]


def test_list_users_filtered_by_environment(
    client: TestClient,
) -> None:
    """Filtra usuários por ambiente."""

    organization, tenant, first_environment = create_hierarchy(client)

    second_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )

    create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(first_environment["id"]),
        name="Usuário de Produção",
        email="producao@deja.com",
    )
    expected_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(second_environment["id"]),
        name="Usuário de Homologação",
        email="homologacao@deja.com",
    )

    response = client.get(
        USERS_URL,
        params={
            "environment_id": second_environment["id"],
        },
    )

    assert response.status_code == 200
    assert response.json() == [expected_user]


def test_list_users_filtered_by_status(
    client: TestClient,
) -> None:
    """Filtra usuários pelo status."""

    organization, tenant, environment = create_hierarchy(client)

    create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Ativo",
        email="ativo@deja.com",
    )
    expected_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Inativo",
        email="inativo@deja.com",
        status="inactive",
    )

    response = client.get(
        USERS_URL,
        params={
            "user_status": "inactive",
        },
    )

    assert response.status_code == 200
    assert response.json() == [expected_user]


def test_get_user_by_id(client: TestClient) -> None:
    """Consulta um usuário pelo identificador."""

    organization, tenant, environment = create_hierarchy(client)

    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
    )

    response = client.get(f"{USERS_URL}/{user['id']}")

    assert response.status_code == 200
    assert response.json() == user


def test_update_user(client: TestClient) -> None:
    """Atualiza integralmente um usuário."""

    organization, tenant, environment = create_hierarchy(client)

    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Principal",
        email="usuario@deja.com",
    )

    response = client.put(
        f"{USERS_URL}/{user['id']}",
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": "  Usuário Atualizado  ",
            "email": "  ATUALIZADO@deja.com  ",
            "role": "analyst",
            "status": "inactive",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == user["id"]
    assert body["organization_id"] == organization["id"]
    assert body["tenant_id"] == tenant["id"]
    assert body["environment_id"] == environment["id"]
    assert body["name"] == "Usuário Atualizado"
    assert body["email"] == "atualizado@deja.com"
    assert body["role"] == "analyst"
    assert body["status"] == "inactive"
    assert body["created_at"] == user["created_at"]
    assert body["updated_at"]


def test_deactivate_user(client: TestClient) -> None:
    """Desativa um usuário por atualização integral."""

    organization, tenant, environment = create_hierarchy(client)

    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
    )

    response = client.put(
        f"{USERS_URL}/{user['id']}",
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "status": "inactive",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "inactive"


def test_create_user_requires_existing_organization(
    client: TestClient,
) -> None:
    """Rejeita usuário de uma organização inexistente."""

    organization_id = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization_id,
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador Órfão",
            "email": "orfao@deja.com",
            "role": "organization_admin",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "organization_not_found"


def test_create_user_requires_existing_tenant(
    client: TestClient,
) -> None:
    """Rejeita usuário vinculado a um tenant inexistente."""

    organization = create_organization(client)
    tenant_id = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant_id,
            "environment_id": None,
            "name": "Usuário Órfão",
            "email": "orfao@deja.com",
            "role": "viewer",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "tenant_not_found"


def test_create_user_requires_existing_environment(
    client: TestClient,
) -> None:
    """Rejeita usuário vinculado a um ambiente inexistente."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment_id = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment_id,
            "name": "Usuário Órfão",
            "email": "orfao@deja.com",
            "role": "viewer",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "environment_not_found"


def test_tenant_must_belong_to_user_organization(
    client: TestClient,
) -> None:
    """Rejeita tenant pertencente a outra organização."""

    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )
    tenant = create_tenant(
        client,
        str(first_organization["id"]),
    )
    client.app.state.set_current_test_organization(str(second_organization["id"]))

    response = client.post(
        USERS_URL,
        json={
            "organization_id": second_organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": None,
            "name": "Usuário Inválido",
            "email": "invalido@deja.com",
            "role": "viewer",
            "status": "active",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == ("tenant_does_not_belong_to_organization")


def test_environment_requires_tenant(
    client: TestClient,
) -> None:
    """Rejeita ambiente informado sem tenant."""

    organization, _, environment = create_hierarchy(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": environment["id"],
            "name": "Usuário Inválido",
            "email": "invalido@deja.com",
            "role": "viewer",
            "status": "active",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "environment_requires_tenant"


def test_environment_must_belong_to_user_tenant(
    client: TestClient,
) -> None:
    """Rejeita ambiente pertencente a outro tenant."""

    organization, first_tenant, environment = create_hierarchy(client)

    second_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Secundário",
    )

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": second_tenant["id"],
            "environment_id": environment["id"],
            "name": "Usuário Inválido",
            "email": "invalido@deja.com",
            "role": "viewer",
            "status": "active",
        },
    )

    assert first_tenant["id"] != second_tenant["id"]
    assert response.status_code == 400
    assert response.json()["error"] == ("environment_does_not_belong_to_tenant")


def test_organization_admin_rejects_tenant_scope(
    client: TestClient,
) -> None:
    """Impede administrador de organização de possuir tenant."""

    organization, tenant, environment = create_hierarchy(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": None,
            "name": "Administrador Inválido",
            "email": "admin@deja.com",
            "role": "organization_admin",
            "status": "active",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "role_scope_mismatch"


def test_tenant_admin_requires_tenant(
    client: TestClient,
) -> None:
    """Exige tenant para administrador de tenant."""

    organization = create_organization(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador Inválido",
            "email": "admin@deja.com",
            "role": "tenant_admin",
            "status": "active",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "role_scope_mismatch"


def test_tenant_admin_rejects_environment_scope(
    client: TestClient,
) -> None:
    """Impede administrador de tenant de possuir ambiente."""

    organization, tenant, environment = create_hierarchy(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": "Administrador Inválido",
            "email": "admin@deja.com",
            "role": "tenant_admin",
            "status": "active",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "role_scope_mismatch"


def test_operational_role_requires_tenant(
    client: TestClient,
) -> None:
    """Exige tenant para papel operacional."""

    organization = create_organization(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Analista Inválido",
            "email": "analista@deja.com",
            "role": "analyst",
            "status": "active",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "role_scope_mismatch"


def test_create_user_rejects_duplicate_email_in_organization(
    client: TestClient,
) -> None:
    """Rejeita e-mail duplicado dentro da mesma organização."""

    organization, tenant, environment = create_hierarchy(client)

    create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="usuario@deja.com",
    )

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": "Outro Usuário",
            "email": "USUARIO@deja.com",
            "role": "viewer",
            "status": "active",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == "user_email_already_exists"


def test_same_email_is_allowed_in_different_organizations(
    client: TestClient,
) -> None:
    """Permite o mesmo e-mail em organizações diferentes."""

    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )

    create_user(
        client,
        str(first_organization["id"]),
        email="admin@deja.com",
        role="organization_admin",
    )

    client.app.state.set_current_test_organization(str(second_organization["id"]))

    response = client.post(
        USERS_URL,
        json={
            "organization_id": second_organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador Secundário",
            "email": "admin@deja.com",
            "role": "organization_admin",
            "status": "active",
        },
    )

    assert response.status_code == 201


def test_update_user_rejects_duplicate_email(
    client: TestClient,
) -> None:
    """Rejeita atualização para o e-mail de outro usuário."""

    organization, tenant, environment = create_hierarchy(client)

    first_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Principal",
        email="principal@deja.com",
    )
    second_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        name="Usuário Secundário",
        email="secundario@deja.com",
    )

    response = client.put(
        f"{USERS_URL}/{second_user['id']}",
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": second_user["name"],
            "email": first_user["email"],
            "role": second_user["role"],
            "status": second_user["status"],
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == "user_email_already_exists"


def test_update_user_keeps_own_email(
    client: TestClient,
) -> None:
    """Permite atualizar um usuário mantendo seu próprio e-mail."""

    organization, tenant, environment = create_hierarchy(client)

    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
    )

    response = client.put(
        f"{USERS_URL}/{user['id']}",
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": "Usuário Renomeado",
            "email": user["email"],
            "role": user["role"],
            "status": user["status"],
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == user["email"]


def test_get_unknown_user_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao consultar um usuário inexistente."""

    user_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(f"{USERS_URL}/{user_id}")

    assert response.status_code == 404
    assert response.json()["error"] == "user_not_found"


def test_update_unknown_user_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao atualizar um usuário inexistente."""

    organization = create_organization(client)
    user_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"{USERS_URL}/{user_id}",
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Usuário Inexistente",
            "email": "inexistente@deja.com",
            "role": "organization_admin",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] == "user_not_found"


def test_create_user_rejects_blank_name(
    client: TestClient,
) -> None:
    """Rejeita nome composto exclusivamente por espaços."""

    organization = create_organization(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "   ",
            "email": "admin@deja.com",
            "role": "organization_admin",
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_create_user_rejects_invalid_email(
    client: TestClient,
) -> None:
    """Rejeita endereço de e-mail inválido."""

    organization = create_organization(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador",
            "email": "email-invalido",
            "role": "organization_admin",
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_create_user_rejects_invalid_role(
    client: TestClient,
) -> None:
    """Rejeita papel não previsto pela Administração de Usuários."""

    organization = create_organization(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador",
            "email": "admin@deja.com",
            "role": "unknown",
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_create_user_rejects_invalid_status(
    client: TestClient,
) -> None:
    """Rejeita status não previsto pela Administração de Usuários."""

    organization = create_organization(client)

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador",
            "email": "admin@deja.com",
            "role": "organization_admin",
            "status": "unknown",
        },
    )

    assert response.status_code == 422


def test_user_id_requires_36_characters(
    client: TestClient,
) -> None:
    """Rejeita identificador que não possui 36 caracteres."""

    response = client.get(f"{USERS_URL}/invalid-id")

    assert response.status_code == 422


def test_user_filters_require_36_characters(
    client: TestClient,
) -> None:
    """Rejeita identificadores institucionais inválidos nos filtros."""

    response = client.get(
        USERS_URL,
        params={
            "organization_id": "invalid-id",
        },
    )

    assert response.status_code == 422


def test_set_user_password_stores_argon2_hash(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Armazena a senha como hash Argon2 sem expor dados sensíveis."""

    organization = create_organization(client)
    user = create_user(
        client,
        organization_id=str(organization["id"]),
        tenant_id=None,
        environment_id=None,
        role="organization_admin",
    )
    plain_password = "SenhaSegura123!"

    response = client.put(
        f"{USERS_URL}/{user['id']}/password",
        json={"password": plain_password},
    )

    assert response.status_code == 200

    body = response.json()

    assert "password" not in body
    assert "password_hash" not in body

    with test_session_factory() as session:
        stored_user = session.get(UserModel, str(user["id"]))

        assert stored_user is not None
        assert stored_user.password_hash is not None
        assert stored_user.password_hash != plain_password
        assert stored_user.password_hash.startswith("$argon2")
        assert PasswordService().verify(
            plain_password,
            stored_user.password_hash,
        )


def test_set_user_password_replaces_existing_hash(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Substitui o hash anterior quando a senha é alterada."""

    organization = create_organization(client)
    user = create_user(
        client,
        organization_id=str(organization["id"]),
        tenant_id=None,
        environment_id=None,
        role="organization_admin",
    )

    first_response = client.put(
        f"{USERS_URL}/{user['id']}/password",
        json={"password": "PrimeiraSenha123!"},
    )

    assert first_response.status_code == 200

    with test_session_factory() as session:
        stored_user = session.get(UserModel, str(user["id"]))

        assert stored_user is not None
        first_hash = stored_user.password_hash

    second_response = client.put(
        f"{USERS_URL}/{user['id']}/password",
        json={"password": "SegundaSenha456!"},
    )

    assert second_response.status_code == 200

    with test_session_factory() as session:
        stored_user = session.get(UserModel, str(user["id"]))

        assert stored_user is not None
        assert stored_user.password_hash != first_hash
        assert PasswordService().verify(
            "SegundaSenha456!",
            stored_user.password_hash,
        )
        assert not PasswordService().verify(
            "PrimeiraSenha123!",
            stored_user.password_hash,
        )


def test_set_user_password_rejects_short_password(
    client: TestClient,
) -> None:
    """Rejeita senha com menos de oito caracteres."""

    organization = create_organization(client)
    user = create_user(
        client,
        organization_id=str(organization["id"]),
        tenant_id=None,
        environment_id=None,
        role="organization_admin",
    )

    response = client.put(
        f"{USERS_URL}/{user['id']}/password",
        json={"password": "curta"},
    )

    assert response.status_code == 422


def test_set_password_for_unknown_user_returns_not_found(
    client: TestClient,
) -> None:
    """Retorna erro ao definir senha para usuário inexistente."""

    user_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"{USERS_URL}/{user_id}/password",
        json={"password": "SenhaSegura123!"},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "user_not_found"
