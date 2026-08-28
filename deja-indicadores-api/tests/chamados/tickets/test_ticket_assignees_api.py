from collections.abc import Mapping
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import (
    authorization_headers,
)
from tests.chamados.tickets.test_ticket_authorization_api import (
    create_scope,
    create_scoped_user,
)

ASSIGNEES_URL = "/api/chamados/tickets/assignees"


@pytest.fixture()
def assignee_context(
    client: TestClient,
    test_settings: Settings,
) -> dict[str, object]:
    """Cria responsáveis elegíveis e usuários que devem ser excluídos."""

    scope = create_scope(client, test_settings)
    organization = scope["organization"]
    tenant = scope["tenant"]
    environment = scope["environment"]

    assert isinstance(organization, dict)
    assert isinstance(tenant, dict)
    assert isinstance(environment, dict)

    organization_admin = create_scoped_user(
        client,
        scope,
        "organization_admin",
    )
    tenant_admin = create_scoped_user(
        client,
        scope,
        "tenant_admin",
    )
    manager = create_scoped_user(
        client,
        scope,
        "manager",
    )
    analyst = create_scoped_user(
        client,
        scope,
        "analyst",
    )
    viewer = create_scoped_user(
        client,
        scope,
        "viewer",
    )

    inactive_analyst = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="analyst.inactive@deja.com",
        role="analyst",
        status="inactive",
    )

    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Ambiente Secundário",
    )
    other_environment_analyst = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(other_environment["id"]),
        email="analyst.other.environment@deja.com",
        role="analyst",
    )

    other_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Secundário",
    )
    other_tenant_analyst = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(other_tenant["id"]),
        email="analyst.other.tenant@deja.com",
        role="analyst",
    )

    return {
        "scope": scope,
        "eligible": [
            organization_admin,
            tenant_admin,
            manager,
            analyst,
        ],
        "viewer": viewer,
        "excluded": [
            inactive_analyst,
            other_environment_analyst,
            other_tenant_analyst,
            scope["platform_admin"],
            viewer,
        ],
    }


def client_id_from(
    context: dict[str, object],
) -> str:
    """Retorna o UUID do Cliente do contexto."""

    scope = context["scope"]
    assert isinstance(scope, dict)

    chamados_client = scope["client"]
    assert isinstance(chamados_client, dict)

    return str(chamados_client["id"])


def test_list_assignees_returns_only_eligible_users(
    client: TestClient,
    assignee_context: dict[str, object],
) -> None:
    """A consulta respeita papel, atividade e escopo do Cliente."""

    scope = assignee_context["scope"]
    eligible = assignee_context["eligible"]
    excluded = assignee_context["excluded"]

    assert isinstance(scope, dict)
    assert isinstance(eligible, list)
    assert isinstance(excluded, list)

    headers = scope["platform_headers"]
    assert isinstance(headers, Mapping)

    response = client.get(
        ASSIGNEES_URL,
        params={
            "client_id": client_id_from(assignee_context),
        },
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()
    returned_ids = {item["id"] for item in body}
    eligible_ids = {str(user["id"]) for user in eligible}
    excluded_ids = {str(user["id"]) for user in excluded}

    assert returned_ids == eligible_ids
    assert returned_ids.isdisjoint(excluded_ids)

    assert all(
        set(item) == {"id", "name", "email", "role"}
        for item in body
    )


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
def test_operational_roles_can_list_assignees(
    client: TestClient,
    test_settings: Settings,
    assignee_context: dict[str, object],
    role: str,
) -> None:
    """Todos os papéis operacionais consultam responsáveis permitidos."""

    scope = assignee_context["scope"]
    assert isinstance(scope, dict)

    if role == "platform_admin":
        user = scope["platform_admin"]
    else:
        user = create_scoped_user(
            client,
            scope,
            role,
            email_suffix="reader",
        )

    assert isinstance(user, dict)

    response = client.get(
        ASSIGNEES_URL,
        params={
            "client_id": client_id_from(assignee_context),
        },
        headers=authorization_headers(test_settings, user),
    )

    assert response.status_code == 200


def test_viewer_cannot_list_assignees(
    client: TestClient,
    test_settings: Settings,
    assignee_context: dict[str, object],
) -> None:
    """O papel somente leitura não recebe opções de atribuição."""

    viewer = assignee_context["viewer"]
    assert isinstance(viewer, dict)

    response = client.get(
        ASSIGNEES_URL,
        params={
            "client_id": client_id_from(assignee_context),
        },
        headers=authorization_headers(test_settings, viewer),
    )

    assert response.status_code == 403


def test_assignees_require_authentication(
    client: TestClient,
    assignee_context: dict[str, object],
) -> None:
    """A consulta rejeita requisições sem token."""

    response = client.get(
        ASSIGNEES_URL,
        params={
            "client_id": client_id_from(assignee_context),
        },
    )

    assert response.status_code == 401


def test_assignees_reject_client_outside_user_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Um usuário institucional não consulta outra organização."""

    first_scope = create_scope(
        client,
        test_settings,
        name="Organização Principal",
        code="ORG-ASSIGNEE-ONE",
    )
    second_scope = create_scope(
        client,
        test_settings,
        name="Organização Externa",
        code="ORG-ASSIGNEE-TWO",
    )
    user = create_scoped_user(
        client,
        first_scope,
        "organization_admin",
    )

    second_client = second_scope["client"]
    assert isinstance(second_client, dict)

    response = client.get(
        ASSIGNEES_URL,
        params={
            "client_id": second_client["id"],
        },
        headers=authorization_headers(test_settings, user),
    )

    assert response.status_code == 403


def test_assignees_return_not_found_for_unknown_client(
    client: TestClient,
    assignee_context: dict[str, object],
) -> None:
    """Um UUID inexistente recebe resposta de recurso não encontrado."""

    scope = assignee_context["scope"]
    assert isinstance(scope, dict)

    headers = scope["platform_headers"]
    assert isinstance(headers, Mapping)

    response = client.get(
        ASSIGNEES_URL,
        params={
            "client_id": str(uuid4()),
        },
        headers=headers,
    )

    assert response.status_code == 404


def test_assignees_reject_invalid_client_id(
    client: TestClient,
    assignee_context: dict[str, object],
) -> None:
    """O contrato rejeita identificadores fora do formato esperado."""

    scope = assignee_context["scope"]
    assert isinstance(scope, dict)

    headers = scope["platform_headers"]
    assert isinstance(headers, Mapping)

    response = client.get(
        ASSIGNEES_URL,
        params={
            "client_id": "cliente-invalido",
        },
        headers=headers,
    )

    assert response.status_code == 422