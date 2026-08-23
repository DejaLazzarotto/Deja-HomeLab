from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.chamados.clients.models import (
    ChamadosClientModel,
)
from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    assert_access_forbidden,
    authorization_headers,
)

CLIENTS_URL = "/api/chamados/clients"

CLIENT_PAYLOAD = {
    "company_name": "Deja Tecnologia Ltda",
    "fantasy_name": "Deja Tecnologia",
    "document": "12345678000190",
    "contact_name": "Maria da Silva",
    "phone": "5432223344",
    "whatsapp": "54999887766",
    "email": "contato@deja.com.br",
    "city": "Caxias do Sul",
    "state": "RS",
    "notes": "",
    "active": True,
}


def insert_client(
    client: TestClient,
    organization_id: str,
    tenant_id: str,
    environment_id: str,
    *,
    fantasy_name: str = "Deja Tecnologia",
    document: str = "12345678000190",
) -> dict[str, str]:
    """Insere um cliente diretamente para os testes."""

    chamados_client = ChamadosClientModel(
        id=str(uuid4()),
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        company_name=f"{fantasy_name} Ltda",
        fantasy_name=fantasy_name,
        document=document,
        contact_name="Maria da Silva",
        phone="5432223344",
        whatsapp="54999887766",
        email="contato@deja.com.br",
        city="Caxias do Sul",
        state="RS",
        notes="",
        active=True,
    )
    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add(chamados_client)
        session.commit()
        session.refresh(chamados_client)

    return {
        "id": chamados_client.id,
        "organization_id": chamados_client.organization_id,
        "tenant_id": chamados_client.tenant_id,
        "environment_id": chamados_client.environment_id,
    }


def create_scoped_user(
    client: TestClient,
    role: str,
    organization_id: str,
    tenant_id: str,
    environment_id: str,
) -> dict[str, object]:
    """Cria uma identidade válida para o escopo informado."""

    if role == "platform_admin":
        return create_user(
            client,
            None,
            email="platform.admin.chamados@deja.com",
            role=role,
        )

    if role == "organization_admin":
        return create_user(
            client,
            organization_id,
            email="organization.admin.chamados@deja.com",
            role=role,
        )

    if role == "tenant_admin":
        return create_user(
            client,
            organization_id,
            tenant_id=tenant_id,
            email="tenant.admin.chamados@deja.com",
            role=role,
        )

    return create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email=f"{role}.chamados@deja.com",
        role=role,
    )


def chamados_client_payload(
    environment_id: str,
    *,
    document: str = "12345678000190",
    fantasy_name: str = "Deja Tecnologia",
) -> dict[str, object]:
    """Cria um payload válido para o ambiente informado."""

    return {
        **CLIENT_PAYLOAD,
        "environment_id": environment_id,
        "document": document,
        "fantasy_name": fantasy_name,
    }


def test_chamados_clients_require_bearer_token(
    client: TestClient,
) -> None:
    """Protege os clientes do módulo com autenticação."""

    response = client.get(CLIENTS_URL)

    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_access_token",
        "message": "Token de acesso inválido.",
    }
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "role",
    [
        "platform_admin",
        "organization_admin",
        "tenant_admin",
        "manager",
        "analyst",
        "viewer",
    ],
)
def test_authorized_roles_read_clients_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite leitura aos papéis autorizados no próprio escopo."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )
    chamados_client = insert_client(
        client,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(
        test_settings,
        user,
    )

    list_response = client.get(
        CLIENTS_URL,
        headers=headers,
    )
    get_response = client.get(
        f"{CLIENTS_URL}/{chamados_client['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [returned_client["id"] for returned_client in list_response.json()] == [
        chamados_client["id"]
    ]
    assert get_response.status_code == 200
    assert get_response.json()["id"] == chamados_client["id"]


@pytest.mark.parametrize(
    "role",
    [
        "platform_admin",
        "organization_admin",
        "tenant_admin",
        "manager",
    ],
)
def test_management_roles_mutate_clients_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite gestão aos papéis administrativos e gestor."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(
        test_settings,
        user,
    )

    create_response = client.post(
        CLIENTS_URL,
        json=chamados_client_payload(str(environment["id"])),
        headers=headers,
    )

    assert create_response.status_code == 201

    client_id = create_response.json()["id"]
    update_response = client.put(
        f"{CLIENTS_URL}/{client_id}",
        json=chamados_client_payload(
            str(environment["id"]),
            fantasy_name="Deja Sistemas",
        ),
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["fantasy_name"] == "Deja Sistemas"

    delete_response = client.delete(
        f"{CLIENTS_URL}/{client_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204


@pytest.mark.parametrize(
    "role",
    [
        "analyst",
        "viewer",
    ],
)
def test_read_only_roles_cannot_mutate_clients(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Nega mutações aos papéis somente de leitura."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )
    chamados_client = insert_client(
        client,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(
        test_settings,
        user,
    )

    create_response = client.post(
        CLIENTS_URL,
        json=chamados_client_payload(
            str(environment["id"]),
            document="98765432000110",
        ),
        headers=headers,
    )
    update_response = client.put(
        f"{CLIENTS_URL}/{chamados_client['id']}",
        json=chamados_client_payload(str(environment["id"])),
        headers=headers,
    )
    delete_response = client.delete(
        f"{CLIENTS_URL}/{chamados_client['id']}",
        headers=headers,
    )

    assert_access_forbidden(create_response)
    assert_access_forbidden(update_response)
    assert_access_forbidden(delete_response)


def test_platform_admin_lists_clients_globally(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite listagem global ao administrador da plataforma."""

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
    first_client = insert_client(
        client,
        str(first_organization["id"]),
        str(first_tenant["id"]),
        str(first_environment["id"]),
    )
    second_client = insert_client(
        client,
        str(second_organization["id"]),
        str(second_tenant["id"]),
        str(second_environment["id"]),
        fantasy_name="Empresa Secundária",
        document="98765432000110",
    )
    administrator = create_user(
        client,
        None,
        email="platform.admin.global.chamados@deja.com",
        role="platform_admin",
    )

    response = client.get(
        CLIENTS_URL,
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 200
    assert {returned_client["id"] for returned_client in response.json()} == {
        first_client["id"],
        second_client["id"],
    }


def test_organization_admin_cannot_cross_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe o administrador à própria organização."""

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
    own_environment = create_environment(
        client,
        str(own_tenant["id"]),
    )
    other_environment = create_environment(
        client,
        str(other_tenant["id"]),
    )
    own_client = insert_client(
        client,
        str(own_organization["id"]),
        str(own_tenant["id"]),
        str(own_environment["id"]),
    )
    other_client = insert_client(
        client,
        str(other_organization["id"]),
        str(other_tenant["id"]),
        str(other_environment["id"]),
        fantasy_name="Empresa Externa",
        document="98765432000110",
    )
    administrator = create_user(
        client,
        str(own_organization["id"]),
        email="organization.admin.isolation@deja.com",
        role="organization_admin",
    )
    headers = authorization_headers(
        test_settings,
        administrator,
    )

    list_response = client.get(
        CLIENTS_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{CLIENTS_URL}/{other_client['id']}",
        headers=headers,
    )
    cross_create_response = client.post(
        CLIENTS_URL,
        json=chamados_client_payload(
            str(other_environment["id"]),
            document="11222333000144",
        ),
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [returned_client["id"] for returned_client in list_response.json()] == [own_client["id"]]
    assert_access_forbidden(cross_get_response)
    assert_access_forbidden(cross_create_response)


def test_tenant_admin_cannot_cross_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe o administrador ao próprio tenant."""

    organization = create_organization(client)
    own_tenant = create_tenant(
        client,
        str(organization["id"]),
    )
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
    own_client = insert_client(
        client,
        str(organization["id"]),
        str(own_tenant["id"]),
        str(own_environment["id"]),
    )
    other_client = insert_client(
        client,
        str(organization["id"]),
        str(other_tenant["id"]),
        str(other_environment["id"]),
        fantasy_name="Empresa Externa",
        document="98765432000110",
    )
    administrator = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(own_tenant["id"]),
        email="tenant.admin.isolation@deja.com",
        role="tenant_admin",
    )
    headers = authorization_headers(
        test_settings,
        administrator,
    )

    list_response = client.get(
        CLIENTS_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{CLIENTS_URL}/{other_client['id']}",
        headers=headers,
    )
    cross_update_response = client.put(
        f"{CLIENTS_URL}/{own_client['id']}",
        json=chamados_client_payload(str(other_environment["id"])),
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [returned_client["id"] for returned_client in list_response.json()] == [own_client["id"]]
    assert_access_forbidden(cross_get_response)
    assert_access_forbidden(cross_update_response)


@pytest.mark.parametrize(
    "role",
    [
        "manager",
        "analyst",
        "viewer",
    ],
)
def test_environment_roles_cannot_cross_environment(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Restringe papéis operacionais ao próprio ambiente."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    own_environment = create_environment(
        client,
        str(tenant["id"]),
    )
    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )
    own_client = insert_client(
        client,
        str(organization["id"]),
        str(tenant["id"]),
        str(own_environment["id"]),
    )
    other_client = insert_client(
        client,
        str(organization["id"]),
        str(tenant["id"]),
        str(other_environment["id"]),
        fantasy_name="Empresa Externa",
        document="98765432000110",
    )
    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(own_environment["id"]),
        email=f"{role}.environment.chamados@deja.com",
        role=role,
    )
    headers = authorization_headers(
        test_settings,
        user,
    )

    list_response = client.get(
        CLIENTS_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{CLIENTS_URL}/{other_client['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [returned_client["id"] for returned_client in list_response.json()] == [own_client["id"]]
    assert_access_forbidden(cross_get_response)


@pytest.mark.parametrize(
    ("role", "filter_name"),
    [
        ("organization_admin", "organization_id"),
        ("tenant_admin", "tenant_id"),
        ("manager", "environment_id"),
        ("analyst", "environment_id"),
        ("viewer", "environment_id"),
    ],
)
def test_limited_roles_cannot_expand_scope_with_filters(
    client: TestClient,
    test_settings: Settings,
    role: str,
    filter_name: str,
) -> None:
    """Nega filtros que tentam ampliar o escopo autenticado."""

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
    own_environment = create_environment(
        client,
        str(own_tenant["id"]),
    )
    other_environment = create_environment(
        client,
        str(other_tenant["id"]),
    )
    user = create_scoped_user(
        client,
        role,
        str(own_organization["id"]),
        str(own_tenant["id"]),
        str(own_environment["id"]),
    )
    forbidden_filter = {
        "organization_id": str(other_organization["id"]),
        "tenant_id": str(other_tenant["id"]),
        "environment_id": str(other_environment["id"]),
    }

    response = client.get(
        CLIENTS_URL,
        params={
            filter_name: forbidden_filter[filter_name],
        },
        headers=authorization_headers(
            test_settings,
            user,
        ),
    )

    assert_access_forbidden(response)
