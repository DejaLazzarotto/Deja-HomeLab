from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.companies.models import (
    CompanyModel,
    CompanyStatus,
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

COMPANIES_URL = "/api/companies"

COMPANY_PAYLOAD = {
    "legal_name": "Deja Tecnologia Ltda",
    "trade_name": "Deja Tecnologia",
    "document": "12345678000190",
    "email": "contato@deja.com.br",
    "phone": "(54) 99999-0000",
    "status": "active",
}


def insert_company(
    client: TestClient,
    environment_id: str,
    *,
    legal_name: str = "Deja Tecnologia Ltda",
    trade_name: str = "Deja Tecnologia",
    document: str = "12345678000190",
) -> dict[str, str]:
    """Insere uma empresa diretamente para os testes de autorização."""

    company = CompanyModel(
        id=str(uuid4()),
        environment_id=environment_id,
        legal_name=legal_name,
        trade_name=trade_name,
        document=document,
        email="contato@deja.com.br",
        phone="(54) 99999-0000",
        status=CompanyStatus.ACTIVE,
    )
    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add(company)
        session.commit()
        session.refresh(company)

    return {
        "id": company.id,
        "environment_id": company.environment_id,
        "legal_name": company.legal_name,
        "trade_name": company.trade_name,
        "document": company.document,
    }


def create_scoped_user(
    client: TestClient,
    role: str,
    organization_id: str,
    tenant_id: str,
    environment_id: str,
) -> dict[str, object]:
    """Cria uma identidade válida para o papel e o escopo informados."""

    if role == "platform_admin":
        return create_user(
            client,
            None,
            email="platform.admin.companies@deja.com",
            role=role,
        )

    if role == "organization_admin":
        return create_user(
            client,
            organization_id,
            email="organization.admin.companies@deja.com",
            role=role,
        )

    if role == "tenant_admin":
        return create_user(
            client,
            organization_id,
            tenant_id=tenant_id,
            email="tenant.admin.companies@deja.com",
            role=role,
        )

    return create_user(
        client,
        organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        email=f"{role}.companies@deja.com",
        role=role,
    )


def company_payload(
    environment_id: str,
    *,
    document: str = "12345678000190",
    trade_name: str = "Deja Tecnologia",
) -> dict[str, str]:
    """Cria um payload válido de empresa para o ambiente informado."""

    return {
        **COMPANY_PAYLOAD,
        "environment_id": environment_id,
        "document": document,
        "trade_name": trade_name,
    }


def test_companies_require_bearer_token(
    client: TestClient,
) -> None:
    """Protege a Gestão de Empresas com autenticação."""

    response = client.get(COMPANIES_URL)

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
def test_all_roles_read_companies_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite leitura de empresas a todos os papéis autorizados."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    company = insert_company(client, str(environment["id"]))
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(test_settings, user)

    list_response = client.get(
        COMPANIES_URL,
        headers=headers,
    )
    get_response = client.get(
        f"{COMPANIES_URL}/{company['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        returned_company["id"]
        for returned_company in list_response.json()
    ] == [company["id"]]
    assert get_response.status_code == 200
    assert get_response.json()["id"] == company["id"]


@pytest.mark.parametrize(
    "role",
    [
        "platform_admin",
        "organization_admin",
        "tenant_admin",
        "manager",
    ],
)
def test_management_roles_mutate_companies_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite gestão de empresas aos papéis administrativos e gestor."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(test_settings, user)

    create_response = client.post(
        COMPANIES_URL,
        json=company_payload(str(environment["id"])),
        headers=headers,
    )

    assert create_response.status_code == 201

    company_id = create_response.json()["id"]
    update_response = client.put(
        f"{COMPANIES_URL}/{company_id}",
        json=company_payload(
            str(environment["id"]),
            trade_name="Deja Sistemas",
        ),
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["trade_name"] == "Deja Sistemas"

    delete_response = client.delete(
        f"{COMPANIES_URL}/{company_id}",
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
def test_read_only_roles_cannot_mutate_companies(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Nega criação, atualização e exclusão a analista e visualizador."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    company = insert_company(client, str(environment["id"]))
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(test_settings, user)

    create_response = client.post(
        COMPANIES_URL,
        json=company_payload(
            str(environment["id"]),
            document="98765432000110",
        ),
        headers=headers,
    )
    update_response = client.put(
        f"{COMPANIES_URL}/{company['id']}",
        json=company_payload(str(environment["id"])),
        headers=headers,
    )
    delete_response = client.delete(
        f"{COMPANIES_URL}/{company['id']}",
        headers=headers,
    )

    assert_access_forbidden(create_response)
    assert_access_forbidden(update_response)
    assert_access_forbidden(delete_response)


def test_platform_admin_lists_companies_globally(
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
    first_company = insert_company(
        client,
        str(first_environment["id"]),
    )
    second_company = insert_company(
        client,
        str(second_environment["id"]),
        legal_name="Empresa Secundária Ltda",
        trade_name="Empresa Secundária",
        document="98765432000110",
    )
    administrator = create_user(
        client,
        None,
        email="platform.admin@deja.com",
        role="platform_admin",
    )

    response = client.get(
        COMPANIES_URL,
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 200
    assert {
        company["id"]
        for company in response.json()
    } == {
        first_company["id"],
        second_company["id"],
    }


def test_organization_admin_is_limited_to_own_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe o administrador organizacional à própria organização."""

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
    own_company = insert_company(
        client,
        str(own_environment["id"]),
    )
    other_company = insert_company(
        client,
        str(other_environment["id"]),
        legal_name="Empresa Externa Ltda",
        trade_name="Empresa Externa",
        document="98765432000110",
    )
    administrator = create_user(
        client,
        str(own_organization["id"]),
        email="organization.admin@deja.com",
    )
    headers = authorization_headers(test_settings, administrator)

    list_response = client.get(
        COMPANIES_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{COMPANIES_URL}/{other_company['id']}",
        headers=headers,
    )
    cross_create_response = client.post(
        COMPANIES_URL,
        json=company_payload(
            str(other_environment["id"]),
            document="11222333000144",
        ),
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        company["id"]
        for company in list_response.json()
    ] == [own_company["id"]]
    assert_access_forbidden(cross_get_response)
    assert_access_forbidden(cross_create_response)


def test_tenant_admin_is_limited_to_own_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe o administrador de tenant ao próprio tenant."""

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
    own_company = insert_company(
        client,
        str(own_environment["id"]),
    )
    other_company = insert_company(
        client,
        str(other_environment["id"]),
        legal_name="Empresa Externa Ltda",
        trade_name="Empresa Externa",
        document="98765432000110",
    )
    administrator = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(own_tenant["id"]),
        email="tenant.admin@deja.com",
        role="tenant_admin",
    )
    headers = authorization_headers(test_settings, administrator)

    list_response = client.get(
        COMPANIES_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{COMPANIES_URL}/{other_company['id']}",
        headers=headers,
    )
    cross_update_response = client.put(
        f"{COMPANIES_URL}/{own_company['id']}",
        json=company_payload(str(other_environment["id"])),
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        company["id"]
        for company in list_response.json()
    ] == [own_company["id"]]
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
    tenant = create_tenant(client, str(organization["id"]))
    own_environment = create_environment(client, str(tenant["id"]))
    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )
    own_company = insert_company(
        client,
        str(own_environment["id"]),
    )
    other_company = insert_company(
        client,
        str(other_environment["id"]),
        legal_name="Empresa Externa Ltda",
        trade_name="Empresa Externa",
        document="98765432000110",
    )
    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(own_environment["id"]),
        email=f"{role}@deja.com",
        role=role,
    )
    headers = authorization_headers(test_settings, user)

    list_response = client.get(
        COMPANIES_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{COMPANIES_URL}/{other_company['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        company["id"]
        for company in list_response.json()
    ] == [own_company["id"]]
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
def test_limited_roles_cannot_expand_list_scope_with_filters(
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
        COMPANIES_URL,
        params={
            filter_name: forbidden_filter[filter_name],
        },
        headers=authorization_headers(test_settings, user),
    )

    assert_access_forbidden(response)