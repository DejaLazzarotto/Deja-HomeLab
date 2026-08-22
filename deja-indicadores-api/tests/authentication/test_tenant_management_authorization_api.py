from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    ENVIRONMENTS_URL,
    ORGANIZATIONS_URL,
    TENANTS_URL,
    USERS_URL,
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    assert_access_forbidden,
    authorization_headers,
)


def test_tenant_management_requires_bearer_token(
    client: TestClient,
) -> None:
    """Protege a Gestão Institucional com autenticação."""

    response = client.get(ORGANIZATIONS_URL)

    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_access_token",
        "message": "Token de acesso inválido.",
    }
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "role",
    [
        "analyst",
        "viewer",
    ],
)
def test_non_administrative_roles_cannot_access_tenant_management(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Nega a Gestão Institucional aos papéis não autorizados."""

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
        ORGANIZATIONS_URL,
        headers=authorization_headers(test_settings, user),
    )

    assert_access_forbidden(response)


def test_platform_admin_manages_global_institutional_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite alcance global ao administrador da plataforma."""

    first_organization = create_organization(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )
    administrator = create_user(
        client,
        None,
        email="platform.admin@deja.com",
        role="platform_admin",
    )
    headers = authorization_headers(test_settings, administrator)

    list_response = client.get(
        ORGANIZATIONS_URL,
        headers=headers,
    )

    assert list_response.status_code == 200
    assert {organization["id"] for organization in list_response.json()} == {
        first_organization["id"],
        second_organization["id"],
    }

    create_response = client.post(
        ORGANIZATIONS_URL,
        json={
            "code": f"ORG-{uuid4().hex[:12].upper()}",
            "name": "Organização Provisionada",
            "status": "active",
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    delete_response = client.delete(
        f"{ORGANIZATIONS_URL}/{create_response.json()['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 204


def test_platform_admin_provisions_organization_administrator(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Completa o provisionamento inicial de uma organização."""

    organization = create_organization(client)
    administrator = create_user(
        client,
        None,
        email="platform.admin@deja.com",
        role="platform_admin",
    )

    response = client.post(
        USERS_URL,
        json={
            "organization_id": organization["id"],
            "tenant_id": None,
            "environment_id": None,
            "name": "Administrador da Organização",
            "email": "organization.admin@deja.com",
            "role": "organization_admin",
            "status": "active",
        },
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 201
    assert response.json()["organization_id"] == organization["id"]
    assert response.json()["role"] == "organization_admin"


def test_organization_admin_is_limited_to_own_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe organização, tenants e ambientes ao próprio escopo."""

    own_organization = create_organization(client)
    other_organization = create_organization(
        client,
        name="Organização Externa",
    )
    own_tenant = create_tenant(
        client,
        str(own_organization["id"]),
    )
    other_tenant = create_tenant(
        client,
        str(other_organization["id"]),
    )
    create_environment(client, str(own_tenant["id"]))
    create_environment(client, str(other_tenant["id"]))
    administrator = create_user(
        client,
        str(own_organization["id"]),
        email="organization.admin@deja.com",
    )
    headers = authorization_headers(test_settings, administrator)

    organization_response = client.get(
        ORGANIZATIONS_URL,
        headers=headers,
    )

    assert organization_response.status_code == 200
    assert [organization["id"] for organization in organization_response.json()] == [
        own_organization["id"]
    ]

    cross_organization_response = client.get(
        f"{ORGANIZATIONS_URL}/{other_organization['id']}",
        headers=headers,
    )

    assert_access_forbidden(cross_organization_response)

    create_tenant_response = client.post(
        TENANTS_URL,
        json={
            "organization_id": own_organization["id"],
            "name": "Tenant Autorizado",
            "status": "active",
        },
        headers=headers,
    )

    assert create_tenant_response.status_code == 201

    cross_tenant_response = client.post(
        TENANTS_URL,
        json={
            "organization_id": other_organization["id"],
            "name": "Tenant Indevido",
            "status": "active",
        },
        headers=headers,
    )

    assert_access_forbidden(cross_tenant_response)

    create_organization_response = client.post(
        ORGANIZATIONS_URL,
        json={
            "code": f"ORG-{uuid4().hex[:12].upper()}",
            "name": "Organização Indevida",
            "status": "active",
        },
        headers=headers,
    )

    assert_access_forbidden(create_organization_response)


def test_organization_admin_cannot_cross_list_filters(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Nega filtros que tentam ampliar o escopo organizacional."""

    own_organization = create_organization(client)
    other_organization = create_organization(
        client,
        name="Organização Externa",
    )
    administrator = create_user(
        client,
        str(own_organization["id"]),
        email="organization.admin@deja.com",
    )
    headers = authorization_headers(test_settings, administrator)

    organizations_response = client.get(
        ORGANIZATIONS_URL,
        params={"organization_id": other_organization["id"]},
        headers=headers,
    )
    tenants_response = client.get(
        TENANTS_URL,
        params={"organization_id": other_organization["id"]},
        headers=headers,
    )
    environments_response = client.get(
        ENVIRONMENTS_URL,
        params={"organization_id": other_organization["id"]},
        headers=headers,
    )

    assert_access_forbidden(organizations_response)
    assert_access_forbidden(tenants_response)
    assert_access_forbidden(environments_response)


def test_tenant_admin_manages_only_own_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite gestão do próprio tenant e de seus ambientes."""

    organization = create_organization(client)
    own_tenant = create_tenant(client, str(organization["id"]))
    other_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Externo",
    )
    own_environment = create_environment(
        client,
        str(own_tenant["id"]),
    )
    other_environment = create_environment(
        client,
        str(other_tenant["id"]),
    )
    administrator = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(own_tenant["id"]),
        email="tenant.admin@deja.com",
        role="tenant_admin",
    )
    headers = authorization_headers(test_settings, administrator)

    own_response = client.get(
        f"{TENANTS_URL}/{own_tenant['id']}",
        headers=headers,
    )
    cross_response = client.get(
        f"{TENANTS_URL}/{other_tenant['id']}",
        headers=headers,
    )

    assert own_response.status_code == 200
    assert_access_forbidden(cross_response)

    update_response = client.put(
        f"{TENANTS_URL}/{own_tenant['id']}",
        json={
            "organization_id": organization["id"],
            "name": "Tenant Atualizado",
            "status": "active",
        },
        headers=headers,
    )

    assert update_response.status_code == 200

    create_environment_response = client.post(
        ENVIRONMENTS_URL,
        json={
            "tenant_id": own_tenant["id"],
            "name": "Homologação",
            "status": "active",
        },
        headers=headers,
    )

    assert create_environment_response.status_code == 201

    cross_environment_response = client.get(
        f"{ENVIRONMENTS_URL}/{other_environment['id']}",
        headers=headers,
    )

    assert_access_forbidden(cross_environment_response)

    create_tenant_response = client.post(
        TENANTS_URL,
        json={
            "organization_id": organization["id"],
            "name": "Tenant Indevido",
            "status": "active",
        },
        headers=headers,
    )

    assert_access_forbidden(create_tenant_response)
    assert own_environment["tenant_id"] == own_tenant["id"]


def test_manager_has_read_only_access_to_own_hierarchy(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite consultas e bloqueia mutações estruturais do gestor."""

    organization = create_organization(client)
    own_tenant = create_tenant(client, str(organization["id"]))
    other_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Externo",
    )
    own_environment = create_environment(
        client,
        str(own_tenant["id"]),
    )
    other_environment = create_environment(
        client,
        str(other_tenant["id"]),
    )
    manager = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(own_tenant["id"]),
        environment_id=str(own_environment["id"]),
        email="manager@deja.com",
        role="manager",
    )
    headers = authorization_headers(test_settings, manager)

    assert (
        client.get(
            f"{ORGANIZATIONS_URL}/{organization['id']}",
            headers=headers,
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"{TENANTS_URL}/{own_tenant['id']}",
            headers=headers,
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"{ENVIRONMENTS_URL}/{own_environment['id']}",
            headers=headers,
        ).status_code
        == 200
    )

    cross_response = client.get(
        f"{ENVIRONMENTS_URL}/{other_environment['id']}",
        headers=headers,
    )

    assert_access_forbidden(cross_response)

    mutation_response = client.put(
        f"{ENVIRONMENTS_URL}/{own_environment['id']}",
        json={
            "tenant_id": own_tenant["id"],
            "name": "Produção Alterada",
            "status": "active",
        },
        headers=headers,
    )

    assert_access_forbidden(mutation_response)
