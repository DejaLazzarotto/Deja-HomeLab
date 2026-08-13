from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.indicators.models import (
    IndicatorDirection,
    IndicatorModel,
    IndicatorStatus,
)
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
)
from tests.authentication.test_company_authorization_api import (
    create_scoped_user,
    insert_company,
)
from tests.authentication.test_user_authorization_api import (
    assert_access_forbidden,
    authorization_headers,
)

INDICATORS_URL = "/api/indicators"


def insert_indicator(
    client: TestClient,
    company_id: str,
    *,
    name: str = "Margem líquida",
) -> dict[str, str]:
    """Insere um indicador diretamente para os testes de autorização."""

    indicator = IndicatorModel(
        id=str(uuid4()),
        company_id=company_id,
        name=name,
        description="Percentual de lucro líquido sobre a receita.",
        unit="%",
        direction=IndicatorDirection.HIGHER_IS_BETTER,
        target_value="15.5000",
        status=IndicatorStatus.ACTIVE,
    )
    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add(indicator)
        session.commit()
        session.refresh(indicator)

    return {
        "id": indicator.id,
        "company_id": indicator.company_id,
        "name": indicator.name,
    }


def indicator_payload(
    company_id: str,
    *,
    name: str = "Margem líquida",
) -> dict[str, str]:
    """Cria um payload válido de indicador."""

    return {
        "company_id": company_id,
        "name": name,
        "description": "Percentual de lucro líquido sobre a receita.",
        "unit": "%",
        "direction": "higher_is_better",
        "target_value": "15.5000",
        "status": "active",
    }


def create_scope(
    client: TestClient,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    """Cria uma hierarquia institucional completa."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))

    return organization, tenant, environment


def test_indicators_require_bearer_token(
    client: TestClient,
) -> None:
    """Protege integralmente as cinco rotas de indicadores."""

    indicator_id = str(uuid4())
    payload = indicator_payload(str(uuid4()))
    responses = [
        client.get(INDICATORS_URL),
        client.get(f"{INDICATORS_URL}/{indicator_id}"),
        client.post(INDICATORS_URL, json=payload),
        client.put(
            f"{INDICATORS_URL}/{indicator_id}",
            json=payload,
        ),
        client.delete(f"{INDICATORS_URL}/{indicator_id}"),
    ]

    for response in responses:
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
def test_all_roles_read_indicators_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite leitura de indicadores a todos os papéis."""

    organization, tenant, environment = create_scope(client)
    company = insert_company(client, str(environment["id"]))
    indicator = insert_indicator(client, company["id"])
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(test_settings, user)

    list_response = client.get(
        INDICATORS_URL,
        headers=headers,
    )
    get_response = client.get(
        f"{INDICATORS_URL}/{indicator['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        returned_indicator["id"]
        for returned_indicator in list_response.json()
    ] == [indicator["id"]]
    assert get_response.status_code == 200
    assert get_response.json()["id"] == indicator["id"]


@pytest.mark.parametrize(
    "role",
    [
        "platform_admin",
        "organization_admin",
        "tenant_admin",
        "manager",
        "analyst",
    ],
)
def test_editor_roles_create_and_update_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite criação e atualização aos gestores e ao analista."""

    organization, tenant, environment = create_scope(client)
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
        INDICATORS_URL,
        json=indicator_payload(company["id"]),
        headers=headers,
    )

    assert create_response.status_code == 201

    indicator_id = create_response.json()["id"]
    update_response = client.put(
        f"{INDICATORS_URL}/{indicator_id}",
        json=indicator_payload(
            company["id"],
            name="Margem operacional",
        ),
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Margem operacional"


@pytest.mark.parametrize(
    "role",
    [
        "platform_admin",
        "organization_admin",
        "tenant_admin",
        "manager",
    ],
)
def test_management_roles_delete_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite exclusão somente aos papéis de gestão."""

    organization, tenant, environment = create_scope(client)
    company = insert_company(client, str(environment["id"]))
    indicator = insert_indicator(client, company["id"])
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )

    response = client.delete(
        f"{INDICATORS_URL}/{indicator['id']}",
        headers=authorization_headers(test_settings, user),
    )

    assert response.status_code == 204


def test_analyst_cannot_delete_indicator(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Nega exclusão estrutural ao analista."""

    organization, tenant, environment = create_scope(client)
    company = insert_company(client, str(environment["id"]))
    indicator = insert_indicator(client, company["id"])
    analyst = create_scoped_user(
        client,
        "analyst",
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )

    response = client.delete(
        f"{INDICATORS_URL}/{indicator['id']}",
        headers=authorization_headers(test_settings, analyst),
    )

    assert_access_forbidden(response)


def test_viewer_cannot_mutate_indicators(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Mantém o visualizador estritamente somente leitura."""

    organization, tenant, environment = create_scope(client)
    company = insert_company(client, str(environment["id"]))
    indicator = insert_indicator(client, company["id"])
    viewer = create_scoped_user(
        client,
        "viewer",
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(test_settings, viewer)
    payload = indicator_payload(company["id"])

    create_response = client.post(
        INDICATORS_URL,
        json=payload,
        headers=headers,
    )
    update_response = client.put(
        f"{INDICATORS_URL}/{indicator['id']}",
        json=payload,
        headers=headers,
    )
    delete_response = client.delete(
        f"{INDICATORS_URL}/{indicator['id']}",
        headers=headers,
    )

    assert_access_forbidden(create_response)
    assert_access_forbidden(update_response)
    assert_access_forbidden(delete_response)


def test_platform_admin_lists_indicators_globally(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite listagem global ao administrador da plataforma."""

    first_organization, first_tenant, first_environment = create_scope(client)
    second_organization = create_organization(
        client,
        name="Organização Secundária",
    )
    second_tenant = create_tenant(
        client,
        str(second_organization["id"]),
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
    first_indicator = insert_indicator(
        client,
        first_company["id"],
    )
    second_indicator = insert_indicator(
        client,
        second_company["id"],
        name="Custo operacional",
    )
    administrator = create_scoped_user(
        client,
        "platform_admin",
        str(first_organization["id"]),
        str(first_tenant["id"]),
        str(first_environment["id"]),
    )

    response = client.get(
        INDICATORS_URL,
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 200
    assert {
        indicator["id"]
        for indicator in response.json()
    } == {
        first_indicator["id"],
        second_indicator["id"],
    }


def test_organization_admin_is_limited_to_own_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe indicadores à organização autenticada."""

    own_organization, own_tenant, own_environment = create_scope(client)
    other_organization = create_organization(
        client,
        name="Organização Externa",
    )
    other_tenant = create_tenant(
        client,
        str(other_organization["id"]),
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
    own_indicator = insert_indicator(client, own_company["id"])
    other_indicator = insert_indicator(
        client,
        other_company["id"],
        name="Custo operacional",
    )
    administrator = create_scoped_user(
        client,
        "organization_admin",
        str(own_organization["id"]),
        str(own_tenant["id"]),
        str(own_environment["id"]),
    )
    headers = authorization_headers(test_settings, administrator)

    list_response = client.get(
        INDICATORS_URL,
        headers=headers,
    )
    get_response = client.get(
        f"{INDICATORS_URL}/{other_indicator['id']}",
        headers=headers,
    )
    create_response = client.post(
        INDICATORS_URL,
        json=indicator_payload(
            other_company["id"],
            name="Receita líquida",
        ),
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        indicator["id"]
        for indicator in list_response.json()
    ] == [own_indicator["id"]]
    assert_access_forbidden(get_response)
    assert_access_forbidden(create_response)


def test_tenant_admin_is_limited_to_own_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe indicadores ao tenant autenticado."""

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
    own_indicator = insert_indicator(client, own_company["id"])
    other_indicator = insert_indicator(
        client,
        other_company["id"],
        name="Custo operacional",
    )
    administrator = create_scoped_user(
        client,
        "tenant_admin",
        str(organization["id"]),
        str(own_tenant["id"]),
        str(own_environment["id"]),
    )
    headers = authorization_headers(test_settings, administrator)

    list_response = client.get(
        INDICATORS_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{INDICATORS_URL}/{other_indicator['id']}",
        headers=headers,
    )
    cross_update_response = client.put(
        f"{INDICATORS_URL}/{own_indicator['id']}",
        json=indicator_payload(other_company["id"]),
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        indicator["id"]
        for indicator in list_response.json()
    ] == [own_indicator["id"]]
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
def test_environment_roles_cannot_read_across_environment(
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
    own_indicator = insert_indicator(client, own_company["id"])
    other_indicator = insert_indicator(
        client,
        other_company["id"],
        name="Custo operacional",
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(own_environment["id"]),
    )
    headers = authorization_headers(test_settings, user)

    list_response = client.get(
        INDICATORS_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{INDICATORS_URL}/{other_indicator['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        indicator["id"]
        for indicator in list_response.json()
    ] == [own_indicator["id"]]
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
    """Nega filtros institucionais que ampliam o escopo autenticado."""

    own_organization, own_tenant, own_environment = create_scope(client)
    other_organization = create_organization(
        client,
        name="Organização Externa",
    )
    other_tenant = create_tenant(
        client,
        str(other_organization["id"]),
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
        INDICATORS_URL,
        params={
            filter_name: forbidden_filter[filter_name],
        },
        headers=authorization_headers(test_settings, user),
    )

    assert_access_forbidden(response)


def test_company_filter_cannot_cross_authenticated_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Nega filtro por empresa localizada fora do escopo autenticado."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    own_environment = create_environment(client, str(tenant["id"]))
    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )
    other_company = insert_company(
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
        INDICATORS_URL,
        params={"company_id": other_company["id"]},
        headers=authorization_headers(test_settings, manager),
    )

    assert_access_forbidden(response)


@pytest.mark.parametrize(
    "role",
    [
        "manager",
        "analyst",
    ],
)
def test_editor_cannot_transfer_indicator_across_environment(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Valida o escopo atual e o destino durante transferências."""

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
    own_indicator = insert_indicator(client, own_company["id"])
    other_indicator = insert_indicator(
        client,
        other_company["id"],
        name="Custo operacional",
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(own_environment["id"]),
    )
    headers = authorization_headers(test_settings, user)

    forbidden_target_response = client.put(
        f"{INDICATORS_URL}/{own_indicator['id']}",
        json=indicator_payload(other_company["id"]),
        headers=headers,
    )
    forbidden_source_response = client.put(
        f"{INDICATORS_URL}/{other_indicator['id']}",
        json=indicator_payload(own_company["id"]),
        headers=headers,
    )

    assert_access_forbidden(forbidden_target_response)
    assert_access_forbidden(forbidden_source_response)


def test_manager_cannot_delete_indicator_outside_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Nega exclusão de indicador localizado em outro ambiente."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    own_environment = create_environment(client, str(tenant["id"]))
    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )
    other_company = insert_company(
        client,
        str(other_environment["id"]),
    )
    other_indicator = insert_indicator(client, other_company["id"])
    manager = create_scoped_user(
        client,
        "manager",
        str(organization["id"]),
        str(tenant["id"]),
        str(own_environment["id"]),
    )

    response = client.delete(
        f"{INDICATORS_URL}/{other_indicator['id']}",
        headers=authorization_headers(test_settings, manager),
    )

    assert_access_forbidden(response)