from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.measurements.models import MeasurementModel
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
from tests.authentication.test_user_authorization_api import (
    assert_access_forbidden,
    authorization_headers,
)

MEASUREMENTS_URL = "/api/measurements"


def insert_measurement(
    client: TestClient,
    indicator_id: str,
    *,
    reference_date: date = date(2026, 8, 1),
    actual_value: str = "87500.2500",
    created_by: str | None = None,
) -> dict[str, str | None]:
    """Insere uma medição diretamente para os testes de autorização."""

    measurement = MeasurementModel(
        id=str(uuid4()),
        indicator_id=indicator_id,
        reference_date=reference_date,
        actual_value=Decimal(actual_value),
        observation="Valor consolidado do período.",
        created_by=created_by,
    )
    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add(measurement)
        session.commit()
        session.refresh(measurement)

    return {
        "id": measurement.id,
        "indicator_id": measurement.indicator_id,
        "created_by": measurement.created_by,
    }


def measurement_payload(
    indicator_id: str,
    *,
    reference_date: str = "2026-08-01",
    actual_value: str = "87500.2500",
) -> dict[str, str]:
    """Cria um payload válido de medição."""

    return {
        "indicator_id": indicator_id,
        "reference_date": reference_date,
        "actual_value": actual_value,
        "observation": "Valor consolidado do período.",
    }


def test_measurements_require_bearer_token(
    client: TestClient,
) -> None:
    """Protege integralmente as cinco rotas de medições."""

    measurement_id = str(uuid4())
    payload = measurement_payload(str(uuid4()))
    responses = [
        client.get(MEASUREMENTS_URL),
        client.get(f"{MEASUREMENTS_URL}/{measurement_id}"),
        client.post(MEASUREMENTS_URL, json=payload),
        client.put(
            f"{MEASUREMENTS_URL}/{measurement_id}",
            json=payload,
        ),
        client.delete(f"{MEASUREMENTS_URL}/{measurement_id}"),
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
def test_all_roles_read_measurements_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite leitura de medições a todos os papéis."""

    organization, tenant, environment = create_scope(client)
    company = insert_company(client, str(environment["id"]))
    indicator = insert_indicator(client, company["id"])
    measurement = insert_measurement(client, indicator["id"])
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(test_settings, user)

    list_response = client.get(
        MEASUREMENTS_URL,
        headers=headers,
    )
    get_response = client.get(
        f"{MEASUREMENTS_URL}/{measurement['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        returned_measurement["id"]
        for returned_measurement in list_response.json()
    ] == [measurement["id"]]
    assert get_response.status_code == 200
    assert get_response.json()["id"] == measurement["id"]


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
def test_editor_roles_manage_measurements_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Permite criação, atualização e exclusão aos papéis operacionais."""

    organization, tenant, environment = create_scope(client)
    company = insert_company(client, str(environment["id"]))
    first_indicator = insert_indicator(client, company["id"])
    second_indicator = insert_indicator(
        client,
        company["id"],
        name="Receita líquida",
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(test_settings, user)

    create_response = client.post(
        MEASUREMENTS_URL,
        json=measurement_payload(first_indicator["id"]),
        headers=headers,
    )

    assert create_response.status_code == 201
    assert create_response.json()["created_by"] == user["id"]

    measurement_id = create_response.json()["id"]
    update_response = client.put(
        f"{MEASUREMENTS_URL}/{measurement_id}",
        json=measurement_payload(
            second_indicator["id"],
            reference_date="2026-08-02",
            actual_value="92500.7500",
        ),
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["indicator_id"] == second_indicator["id"]
    assert update_response.json()["created_by"] == user["id"]

    delete_response = client.delete(
        f"{MEASUREMENTS_URL}/{measurement_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204


def test_viewer_cannot_mutate_measurements(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Mantém o visualizador estritamente somente leitura."""

    organization, tenant, environment = create_scope(client)
    company = insert_company(client, str(environment["id"]))
    indicator = insert_indicator(client, company["id"])
    measurement = insert_measurement(client, indicator["id"])
    viewer = create_scoped_user(
        client,
        "viewer",
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )
    headers = authorization_headers(test_settings, viewer)
    payload = measurement_payload(indicator["id"])

    create_response = client.post(
        MEASUREMENTS_URL,
        json=payload,
        headers=headers,
    )
    update_response = client.put(
        f"{MEASUREMENTS_URL}/{measurement['id']}",
        json=payload,
        headers=headers,
    )
    delete_response = client.delete(
        f"{MEASUREMENTS_URL}/{measurement['id']}",
        headers=headers,
    )

    assert_access_forbidden(create_response)
    assert_access_forbidden(update_response)
    assert_access_forbidden(delete_response)


def test_platform_admin_lists_measurements_globally(
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
    first_indicator = insert_indicator(client, first_company["id"])
    second_indicator = insert_indicator(
        client,
        second_company["id"],
        name="Custo operacional",
    )
    first_measurement = insert_measurement(
        client,
        first_indicator["id"],
    )
    second_measurement = insert_measurement(
        client,
        second_indicator["id"],
    )
    administrator = create_scoped_user(
        client,
        "platform_admin",
        str(first_organization["id"]),
        str(first_tenant["id"]),
        str(first_environment["id"]),
    )

    response = client.get(
        MEASUREMENTS_URL,
        headers=authorization_headers(
            test_settings,
            administrator,
        ),
    )

    assert response.status_code == 200
    assert {
        measurement["id"]
        for measurement in response.json()
    } == {
        first_measurement["id"],
        second_measurement["id"],
    }


def test_organization_admin_is_limited_to_own_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe medições à organização autenticada."""

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
    own_company = insert_company(client, str(own_environment["id"]))
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
    own_measurement = insert_measurement(client, own_indicator["id"])
    other_measurement = insert_measurement(
        client,
        other_indicator["id"],
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
        MEASUREMENTS_URL,
        headers=headers,
    )
    get_response = client.get(
        f"{MEASUREMENTS_URL}/{other_measurement['id']}",
        headers=headers,
    )
    create_response = client.post(
        MEASUREMENTS_URL,
        json=measurement_payload(
            other_indicator["id"],
            reference_date="2026-08-02",
        ),
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        measurement["id"]
        for measurement in list_response.json()
    ] == [own_measurement["id"]]
    assert_access_forbidden(get_response)
    assert_access_forbidden(create_response)


def test_tenant_admin_is_limited_to_own_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Restringe medições ao tenant autenticado."""

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
    own_company = insert_company(client, str(own_environment["id"]))
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
    own_measurement = insert_measurement(client, own_indicator["id"])
    other_measurement = insert_measurement(
        client,
        other_indicator["id"],
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
        MEASUREMENTS_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{MEASUREMENTS_URL}/{other_measurement['id']}",
        headers=headers,
    )
    cross_update_response = client.put(
        f"{MEASUREMENTS_URL}/{own_measurement['id']}",
        json=measurement_payload(other_indicator["id"]),
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        measurement["id"]
        for measurement in list_response.json()
    ] == [own_measurement["id"]]
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
    own_company = insert_company(client, str(own_environment["id"]))
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
    own_measurement = insert_measurement(client, own_indicator["id"])
    other_measurement = insert_measurement(
        client,
        other_indicator["id"],
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
        MEASUREMENTS_URL,
        headers=headers,
    )
    cross_get_response = client.get(
        f"{MEASUREMENTS_URL}/{other_measurement['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [
        measurement["id"]
        for measurement in list_response.json()
    ] == [own_measurement["id"]]
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
        MEASUREMENTS_URL,
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
def test_resource_filter_cannot_cross_authenticated_scope(
    client: TestClient,
    test_settings: Settings,
    filter_name: str,
) -> None:
    """Nega filtro por empresa ou indicador fora do escopo autenticado."""

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
    filter_value = {
        "company_id": other_company["id"],
        "indicator_id": other_indicator["id"],
    }

    response = client.get(
        MEASUREMENTS_URL,
        params={filter_name: filter_value[filter_name]},
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
def test_editor_cannot_transfer_measurement_across_environment(
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
    own_company = insert_company(client, str(own_environment["id"]))
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
    own_measurement = insert_measurement(client, own_indicator["id"])
    other_measurement = insert_measurement(
        client,
        other_indicator["id"],
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
        f"{MEASUREMENTS_URL}/{own_measurement['id']}",
        json=measurement_payload(other_indicator["id"]),
        headers=headers,
    )
    forbidden_source_response = client.put(
        f"{MEASUREMENTS_URL}/{other_measurement['id']}",
        json=measurement_payload(own_indicator["id"]),
        headers=headers,
    )

    assert_access_forbidden(forbidden_target_response)
    assert_access_forbidden(forbidden_source_response)


@pytest.mark.parametrize(
    "role",
    [
        "manager",
        "analyst",
    ],
)
def test_editor_cannot_delete_measurement_outside_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Nega exclusão de medição localizada em outro ambiente."""

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
    other_measurement = insert_measurement(
        client,
        other_indicator["id"],
    )
    user = create_scoped_user(
        client,
        role,
        str(organization["id"]),
        str(tenant["id"]),
        str(own_environment["id"]),
    )

    response = client.delete(
        f"{MEASUREMENTS_URL}/{other_measurement['id']}",
        headers=authorization_headers(test_settings, user),
    )

    assert_access_forbidden(response)


def test_platform_admin_applies_all_institutional_filters(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Permite ao administrador global combinar filtros institucionais."""

    organization, tenant, environment = create_scope(client)
    company = insert_company(client, str(environment["id"]))
    indicator = insert_indicator(client, company["id"])
    measurement = insert_measurement(client, indicator["id"])
    administrator = create_scoped_user(
        client,
        "platform_admin",
        str(organization["id"]),
        str(tenant["id"]),
        str(environment["id"]),
    )

    response = client.get(
        MEASUREMENTS_URL,
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
    assert [
        returned_measurement["id"]
        for returned_measurement in response.json()
    ] == [measurement["id"]]