from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
)
from tests.authentication.test_company_authorization_api import (
    create_scoped_user,
    insert_company,
)
from tests.authentication.test_indicator_authorization_api import (
    create_scope,
    insert_indicator,
)
from tests.authentication.test_measurement_authorization_api import (
    insert_measurement,
)
from tests.authentication.test_user_authorization_api import (
    assert_access_forbidden,
    authorization_headers,
)

DASHBOARD_URL = "/api/dashboards/overview"


def insert_dashboard_data(
    client: TestClient,
    environment_id: str,
    *,
    legal_name: str = "Empresa Principal Ltda",
    trade_name: str = "Empresa Principal",
    document: str = "12345678000190",
    indicator_name: str = "Receita operacional",
) -> tuple[dict, dict, dict]:
    """Insere empresa, indicador e medição para o dashboard."""

    company = insert_company(
        client,
        environment_id,
        legal_name=legal_name,
        trade_name=trade_name,
        document=document,
    )
    indicator = insert_indicator(
        client,
        company["id"],
        name=indicator_name,
    )
    measurement = insert_measurement(
        client,
        indicator["id"],
    )

    return company, indicator, measurement


def assert_single_dashboard_scope(
    data: dict,
    *,
    company_id: str,
    indicator_id: str,
    measurement_id: str,
) -> None:
    """Confirma que a agregação contém somente um escopo esperado."""

    assert data["totals"] == {
        "companies": 1,
        "indicators": 1,
        "measurements": 1,
    }
    assert len(data["indicators"]) == 1

    returned_indicator = data["indicators"][0]

    assert returned_indicator["company_id"] == company_id
    assert returned_indicator["id"] == indicator_id
    assert [
        measurement["id"]
        for measurement in returned_indicator["history"]
    ] == [measurement_id]


def test_dashboard_requires_bearer_token(
    client: TestClient,
) -> None:
    """Protege a rota de visão geral com autenticação Bearer."""

    response = client.get(DASHBOARD_URL)

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
def test_all_roles_read_dashboard_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite leitura do dashboard aos seis papéis."""

    organization, tenant, environment = create_scope(client)
    company, indicator, measurement = insert_dashboard_data(
        client,
        str(environment["id"]),
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        headers=authorization_headers(test_settings, user),
    )

    assert response.status_code == 200
    assert_single_dashboard_scope(
        response.json(),
        company_id=company["id"],
        indicator_id=indicator["id"],
        measurement_id=measurement["id"],
    )


def test_platform_admin_reads_dashboard_globally(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite agregação global ao administrador da plataforma."""

    first_organization, first_tenant, first_environment = create_scope(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )
    second_tenant = create_tenant(
        client,
        str(second_organization["id"]),
        name="Tenant Secundário",
    )
    second_environment = create_environment(
        client,
        str(second_tenant["id"]),
        name="Produção Secundária",
    )
    first_company, first_indicator, _ = insert_dashboard_data(
        client,
        str(first_environment["id"]),
    )
    second_company, second_indicator, _ = insert_dashboard_data(
        client,
        str(second_environment["id"]),
        legal_name="Empresa Secundária Ltda",
        trade_name="Empresa Secundária",
        document="98765432000110",
        indicator_name="Custo operacional",
    )
    administrator = create_scoped_user(
        client,
        "platform_admin",
        str(first_organization["id"]),
        str(first_tenant["id"]),
        str(first_environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["totals"] == {
        "companies": 2,
        "indicators": 2,
        "measurements": 2,
    }
    assert {
        indicator["company_id"]
        for indicator in data["indicators"]
    } == {
        first_company["id"],
        second_company["id"],
    }
    assert {
        indicator["id"]
        for indicator in data["indicators"]
    } == {
        first_indicator["id"],
        second_indicator["id"],
    }


def test_organization_admin_reads_only_own_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe todas as agregações à organização autenticada."""

    own_organization, own_tenant, own_environment = create_scope(client)
    other_organization = create_organization(
        client,
        name="Organização Externa",
    )
    other_tenant = create_tenant(
        client,
        str(other_organization["id"]),
        name="Tenant Externo",
    )
    other_environment = create_environment(
        client,
        str(other_tenant["id"]),
        name="Produção Externa",
    )
    own_company, own_indicator, own_measurement = insert_dashboard_data(
        client,
        str(own_environment["id"]),
    )
    insert_dashboard_data(
        client,
        str(other_environment["id"]),
        legal_name="Empresa Externa Ltda",
        trade_name="Empresa Externa",
        document="98765432000110",
        indicator_name="Custo operacional",
    )
    administrator = create_scoped_user(
        client,
        "organization_admin",
        str(own_organization["id"]),
        str(own_tenant["id"]),
        str(own_environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 200
    assert_single_dashboard_scope(
        response.json(),
        company_id=own_company["id"],
        indicator_id=own_indicator["id"],
        measurement_id=own_measurement["id"],
    )


def test_tenant_admin_reads_only_own_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe todas as agregações ao tenant autenticado."""

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
        name="Produção Externa",
    )
    own_company, own_indicator, own_measurement = insert_dashboard_data(
        client,
        str(own_environment["id"]),
    )
    insert_dashboard_data(
        client,
        str(other_environment["id"]),
        legal_name="Empresa Externa Ltda",
        trade_name="Empresa Externa",
        document="98765432000110",
        indicator_name="Custo operacional",
    )
    administrator = create_scoped_user(
        client,
        "tenant_admin",
        str(organization["id"]),
        str(own_tenant["id"]),
        str(own_environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 200
    assert_single_dashboard_scope(
        response.json(),
        company_id=own_company["id"],
        indicator_id=own_indicator["id"],
        measurement_id=own_measurement["id"],
    )


@pytest.mark.parametrize(
    "role",
    [
        "manager",
        "analyst",
        "viewer",
    ],
)
def test_environment_roles_read_only_own_environment(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Restringe papéis operacionais ao ambiente autenticado."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    own_environment = create_environment(client, str(tenant["id"]))
    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )
    own_company, own_indicator, own_measurement = insert_dashboard_data(
        client,
        str(own_environment["id"]),
    )
    insert_dashboard_data(
        client,
        str(other_environment["id"]),
        legal_name="Empresa Externa Ltda",
        trade_name="Empresa Externa",
        document="98765432000110",
        indicator_name="Custo operacional",
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(own_environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        headers=authorization_headers(test_settings, user),
    )

    assert response.status_code == 200
    assert_single_dashboard_scope(
        response.json(),
        company_id=own_company["id"],
        indicator_id=own_indicator["id"],
        measurement_id=own_measurement["id"],
    )


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
def test_limited_roles_cannot_expand_dashboard_scope_with_filters(
    client: TestClient,
    test_settings: Settings,
    role: str,
    filter_name: str,
) -> None:
    """Nega filtros institucionais que ampliam o escopo autenticado."""

    own_organization, own_tenant, own_environment = create_scope(client)
    other_organization = create_organization(
        client,
        name="Organização Externa",
    )
    other_tenant = create_tenant(
        client,
        str(other_organization["id"]),
        name="Tenant Externo",
    )
    other_environment = create_environment(
        client,
        str(other_tenant["id"]),
        name="Produção Externa",
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
        DASHBOARD_URL,
        params={
            filter_name: forbidden_filter[filter_name],
        },
        headers=authorization_headers(test_settings, user),
    )

    assert_access_forbidden(response)


@pytest.mark.parametrize(
    "filter_name",
    [
        "company_id",
        "indicator_id",
    ],
)
def test_resource_filter_cannot_cross_dashboard_scope(
    client: TestClient,
    test_settings: Settings,
    filter_name: str,
) -> None:
    """Nega filtro por empresa ou indicador fora do escopo."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    own_environment = create_environment(client, str(tenant["id"]))
    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )
    other_company, other_indicator, _ = insert_dashboard_data(
        client,
        str(other_environment["id"]),
    )
    manager = create_scoped_user(
        client,
        "manager",
        str(organization["id"]),
        str(tenant["id"]),
        str(own_environment["id"]),
    )
    filter_value = {
        "company_id": other_company["id"],
        "indicator_id": other_indicator["id"],
    }

    response = client.get(
        DASHBOARD_URL,
        params={filter_name: filter_value[filter_name]},
        headers=authorization_headers(test_settings, manager),
    )

    assert_access_forbidden(response)


def test_platform_admin_combines_all_dashboard_filters(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite ao administrador global combinar todos os filtros."""

    organization, tenant, environment = create_scope(client)
    company, indicator, measurement = insert_dashboard_data(
        client,
        str(environment["id"]),
    )
    administrator = create_scoped_user(
        client,
        "platform_admin",
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        params={
            "organization_id": organization["id"],
            "tenant_id": tenant["id"],
            "environment_id": environment["id"],
            "company_id": company["id"],
            "indicator_id": indicator["id"],
            "start_date": "2026-08-01",
            "end_date": "2026-08-01",
        },
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 200
    assert_single_dashboard_scope(
        response.json(),
        company_id=company["id"],
        indicator_id=indicator["id"],
        measurement_id=measurement["id"],
    )


def test_dashboard_is_empty_inside_scope_without_data(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Retorna vazio sem incorporar dados de outro ambiente."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    own_environment = create_environment(client, str(tenant["id"]))
    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )
    insert_dashboard_data(
        client,
        str(other_environment["id"]),
    )
    manager = create_scoped_user(
        client,
        "manager",
        str(organization["id"]),
        str(tenant["id"]),
        str(own_environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        headers=authorization_headers(test_settings, manager),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["totals"] == {
        "companies": 0,
        "indicators": 0,
        "measurements": 0,
    }
    assert data["companies_by_status"] == []
    assert data["indicators_by_status"] == []
    assert data["indicators"] == []


def test_mismatched_company_and_indicator_filters_return_empty_dashboard(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Retorna vazio para recursos autorizados sem relação entre si."""

    organization, tenant, environment = create_scope(client)
    first_company, _, _ = insert_dashboard_data(
        client,
        str(environment["id"]),
    )
    second_company = insert_company(
        client,
        str(environment["id"]),
        legal_name="Empresa Secundária Ltda",
        trade_name="Empresa Secundária",
        document="98765432000110",
    )
    second_indicator = insert_indicator(
        client,
        second_company["id"],
        name="Custo operacional",
    )
    manager = create_scoped_user(
        client,
        "manager",
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        params={
            "company_id": first_company["id"],
            "indicator_id": second_indicator["id"],
        },
        headers=authorization_headers(test_settings, manager),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["totals"] == {
        "companies": 0,
        "indicators": 0,
        "measurements": 0,
    }
    assert data["companies_by_status"] == []
    assert data["indicators_by_status"] == []
    assert data["indicators"] == []


def test_dashboard_rejects_unknown_indicator(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita filtro por indicador inexistente."""

    organization, tenant, environment = create_scope(client)
    manager = create_scoped_user(
        client,
        "manager",
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )

    response = client.get(
        DASHBOARD_URL,
        params={
            "indicator_id": str(uuid4()),
        },
        headers=authorization_headers(test_settings, manager),
    )

    assert response.status_code == 404
    assert response.json()["error"] == "indicator_not_found"