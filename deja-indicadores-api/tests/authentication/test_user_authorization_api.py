from collections.abc import Mapping

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    TENANTS_URL,
    USERS_URL,
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_current_user_api import (
    create_signed_token,
)


def authorization_headers(
    settings: Settings,
    user: dict[str, object],
) -> Mapping[str, str]:
    """Cria o cabeçalho Bearer de um usuário persistido."""

    token = create_signed_token(settings, user)

    return {"Authorization": f"Bearer {token}"}


def create_named_tenant(
    client: TestClient,
    organization_id: str,
    name: str,
) -> dict[str, object]:
    """Cadastra um tenant com nome controlado."""

    response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization_id,
            "name": name,
            "status": "active",
        },
    )

    assert response.status_code == 201, response.text
    return response.json()


def assert_access_forbidden(response: object) -> None:
    """Valida o contrato público de autorização negada."""

    assert hasattr(response, "status_code")
    assert response.status_code == 403
    assert response.json() == {
        "error": "access_forbidden",
        "message": "Acesso não permitido.",
    }
    assert "www-authenticate" not in response.headers


def test_users_require_bearer_token(
    client: TestClient,
) -> None:
    """Protege a Administração de Usuários com autenticação."""

    response = client.get(USERS_URL)

    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_access_token",
        "message": "Token de acesso inválido.",
    }
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "role",
    [
        "manager",
        "analyst",
        "viewer",
    ],
)
def test_operational_roles_cannot_administer_users(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Nega Administração de Usuários aos papéis operacionais."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email=f"{role}@deja.com",
        role=role,
    )

    response = client.get(
        USERS_URL,
        headers=authorization_headers(test_settings, user),
    )

    assert_access_forbidden(response)


def test_organization_admin_lists_only_own_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Limita o administrador ao escopo da própria organização."""

    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )
    administrator = create_user(
        client,
        str(first_organization["id"]),
        email="admin.principal@deja.com",
    )
    own_user = create_user(
        client,
        str(first_organization["id"]),
        email="usuario.principal@deja.com",
    )
    other_user = create_user(
        client,
        str(second_organization["id"]),
        email="usuario.secundario@deja.com",
    )
    headers = authorization_headers(
        test_settings,
        administrator,
    )

    response = client.get(
        USERS_URL,
        headers=headers,
    )

    assert response.status_code == 200

    returned_ids = {
        user["id"]
        for user in response.json()
    }

    assert administrator["id"] in returned_ids
    assert own_user["id"] in returned_ids
    assert other_user["id"] not in returned_ids

    cross_scope_response = client.get(
        USERS_URL,
        params={
            "organization_id": second_organization["id"],
        },
        headers=headers,
    )

    assert_access_forbidden(cross_scope_response)


def test_organization_admin_manages_any_scope_in_own_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite alcance integral dentro da própria organização."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    administrator = create_user(
        client,
        str(organization["id"]),
        email="admin@deja.com",
    )

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "name": "Analista Autorizado",
            "email": "analista.autorizado@deja.com",
            "role": "analyst",
            "status": "active",
        },
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 201
    assert response.json()["tenant_id"] == tenant["id"]
    assert response.json()["environment_id"] == environment["id"]


def test_organization_admin_cannot_cross_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Impede criação de usuário em outra organização."""

    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )
    administrator = create_user(
        client,
        str(first_organization["id"]),
        email="admin@deja.com",
    )

    response = client.post(
        USERS_URL,
        json={
            "organization_id": second_organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador Indevido",
            "email": "admin.indevido@deja.com",
            "role": "organization_admin",
            "status": "active",
        },
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert_access_forbidden(response)


def test_tenant_admin_lists_and_reads_only_own_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe listagem e consulta ao tenant autenticado."""

    organization = create_organization(client)
    first_tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    second_tenant = create_named_tenant(
        client,
        str(organization["id"]),
        "Tenant Secundário",
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
        str(organization["id"]),
        tenant_id=str(first_tenant["id"]),
        email="tenant.admin@deja.com",
        role="tenant_admin",
    )
    own_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(first_tenant["id"]),
        environment_id=str(first_environment["id"]),
        email="proprio@deja.com",
        role="viewer",
    )
    other_user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(second_tenant["id"]),
        environment_id=str(second_environment["id"]),
        email="externo@deja.com",
        role="viewer",
    )
    headers = authorization_headers(
        test_settings,
        administrator,
    )

    response = client.get(
        USERS_URL,
        headers=headers,
    )

    assert response.status_code == 200

    returned_ids = {
        user["id"]
        for user in response.json()
    }

    assert administrator["id"] in returned_ids
    assert own_user["id"] in returned_ids
    assert other_user["id"] not in returned_ids

    cross_scope_response = client.get(
        f"{USERS_URL}/{other_user['id']}",
        headers=headers,
    )

    assert_access_forbidden(cross_scope_response)


def test_tenant_admin_cannot_manage_organization_admin(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Impede elevação para o escopo da organização."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    administrator = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        email="tenant.admin@deja.com",
        role="tenant_admin",
    )

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador Geral",
            "email": "organization.admin@deja.com",
            "role": "organization_admin",
            "status": "active",
        },
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert_access_forbidden(response)


def test_tenant_admin_cannot_move_user_to_another_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Impede alteração que mova usuário para outro tenant."""

    organization = create_organization(client)
    first_tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    second_tenant = create_named_tenant(
        client,
        str(organization["id"]),
        "Tenant Secundário",
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
        str(organization["id"]),
        tenant_id=str(first_tenant["id"]),
        email="tenant.admin@deja.com",
        role="tenant_admin",
    )
    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(first_tenant["id"]),
        environment_id=str(first_environment["id"]),
        email="usuario@deja.com",
        role="viewer",
    )

    response = client.put(
        f"{USERS_URL}/{user['id']}",
        json={
            "organization_id": organization["id"],
            "tenant_id": second_tenant["id"],
            "environment_id": second_environment["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "status": user["status"],
        },
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert_access_forbidden(response)