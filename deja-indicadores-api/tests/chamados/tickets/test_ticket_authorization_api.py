from collections.abc import Mapping

import pytest
from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from tests.authentication.test_authentication_api import (
    create_environment,
    create_organization,
    create_tenant,
    create_user,
)
from tests.authentication.test_user_authorization_api import authorization_headers
from tests.chamados.clients.test_clients_api import FIRST_CLIENT, SECOND_CLIENT, create_client
from tests.chamados.tickets.test_tickets_api import TICKETS_URL

ACTIVE_SECOND_CLIENT = {
    **SECOND_CLIENT,
    "active": True,
}


def create_scope(
    client: TestClient,
    test_settings: Settings,
    *,
    name: str = "Organização Chamados",
    code: str = "ORG-CHAMADOS",
    enabled_modules: set[str] | None = None,
    client_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    """Cria um escopo completo e um Cliente usando a identidade global."""

    organization = create_organization(
        client,
        name=name,
        code=code,
        enabled_modules=enabled_modules,
    )
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    platform_admin = create_user(
        client,
        None,
        email=f"platform.{code.lower()}@deja.com",
        role="platform_admin",
    )
    platform_headers = authorization_headers(test_settings, platform_admin)
    chamados_client = create_client(
        client,
        client_payload or FIRST_CLIENT,
        str(environment["id"]),
        platform_headers,
    )

    return {
        "organization": organization,
        "tenant": tenant,
        "environment": environment,
        "platform_admin": platform_admin,
        "platform_headers": platform_headers,
        "client": chamados_client,
    }


def create_scoped_user(
    client: TestClient,
    scope: dict[str, object],
    role: str,
    *,
    email_suffix: str = "principal",
) -> dict[str, object]:
    """Cria um usuário com o alcance institucional típico do papel."""

    organization = scope["organization"]
    tenant = scope["tenant"]
    environment = scope["environment"]
    assert isinstance(organization, dict)
    assert isinstance(tenant, dict)
    assert isinstance(environment, dict)

    tenant_id = None
    environment_id = None

    if role in {"tenant_admin", "manager", "analyst", "viewer"}:
        tenant_id = str(tenant["id"])

    if role in {"manager", "analyst", "viewer"}:
        environment_id = str(environment["id"])

    return create_user(
        client,
        str(organization["id"]),
        tenant_id=tenant_id,
        environment_id=environment_id,
        email=f"{role}.{email_suffix}@deja.com",
        role=role,
    )


def create_ticket_as_platform(
    client: TestClient,
    scope: dict[str, object],
    **overrides: object,
) -> dict[str, object]:
    """Abre um chamado dentro do escopo usando o administrador global."""

    environment = scope["environment"]
    chamados_client = scope["client"]
    platform_headers = scope["platform_headers"]
    assert isinstance(environment, dict)
    assert isinstance(chamados_client, dict)
    assert isinstance(platform_headers, Mapping)

    response = client.post(
        TICKETS_URL,
        json={
            "environment_id": environment["id"],
            "client_id": chamados_client["id"],
            "title": "Chamado para autorização",
            "description": "Validação do escopo institucional.",
            "priority": "medium",
            "assigned_to_user_id": None,
            **overrides,
        },
        headers=platform_headers,
    )

    assert response.status_code == 201
    return response.json()


def test_chamados_tickets_require_bearer_token(
    client: TestClient,
) -> None:
    """As rotas não aceitam requisições anônimas."""

    response = client.get(TICKETS_URL)

    assert response.status_code == 401


@pytest.mark.parametrize(
    "role",
    [
        "organization_admin",
        "tenant_admin",
        "manager",
        "analyst",
        "viewer",
    ],
)
def test_authorized_roles_read_tickets_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Papéis internos autorizados consultam chamados no próprio alcance."""

    scope = create_scope(client, test_settings)
    ticket = create_ticket_as_platform(client, scope)
    user = create_scoped_user(client, scope, role)
    headers = authorization_headers(test_settings, user)

    list_response = client.get(TICKETS_URL, headers=headers)
    get_response = client.get(
        f"{TICKETS_URL}/{ticket['id']}",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [ticket["id"]]
    assert get_response.status_code == 200
    assert get_response.json()["id"] == ticket["id"]


@pytest.mark.parametrize(
    "role",
    [
        "organization_admin",
        "tenant_admin",
        "manager",
        "analyst",
    ],
)
def test_operator_roles_mutate_tickets_inside_own_scope(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Papéis operacionais abrem, atualizam e encerram chamados."""

    scope = create_scope(client, test_settings)
    user = create_scoped_user(client, scope, role)
    headers = authorization_headers(test_settings, user)
    environment = scope["environment"]
    chamados_client = scope["client"]
    assert isinstance(environment, dict)
    assert isinstance(chamados_client, dict)

    create_response = client.post(
        TICKETS_URL,
        json={
            "environment_id": environment["id"],
            "client_id": chamados_client["id"],
            "title": "Chamado operacional",
            "description": "Aberto por um usuário interno.",
            "priority": "medium",
            "assigned_to_user_id": user["id"],
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    ticket = create_response.json()
    assert ticket["opened_by_user_id"] == user["id"]

    update_response = client.put(
        f"{TICKETS_URL}/{ticket['id']}",
        json={
            "title": "Chamado operacional atualizado",
            "description": "Atendimento em execução.",
            "priority": "high",
            "assigned_to_user_id": user["id"],
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["priority"] == "high"

    status_response = client.patch(
        f"{TICKETS_URL}/{ticket['id']}/status",
        json={"status": "closed"},
        headers=headers,
    )
    assert status_response.status_code == 200
    assert status_response.json()["closed_by_user_id"] == user["id"]


def test_viewer_cannot_mutate_tickets(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Viewer consulta chamados, mas não executa operações."""

    scope = create_scope(client, test_settings)
    ticket = create_ticket_as_platform(client, scope)
    viewer = create_scoped_user(client, scope, "viewer")
    headers = authorization_headers(test_settings, viewer)
    environment = scope["environment"]
    chamados_client = scope["client"]
    assert isinstance(environment, dict)
    assert isinstance(chamados_client, dict)

    create_response = client.post(
        TICKETS_URL,
        json={
            "environment_id": environment["id"],
            "client_id": chamados_client["id"],
            "title": "Operação proibida",
            "description": "Viewer não pode abrir chamado interno.",
        },
        headers=headers,
    )
    update_response = client.put(
        f"{TICKETS_URL}/{ticket['id']}",
        json={
            "title": "Operação proibida",
            "description": "Viewer não pode atualizar.",
            "priority": "low",
            "assigned_to_user_id": None,
        },
        headers=headers,
    )
    status_response = client.patch(
        f"{TICKETS_URL}/{ticket['id']}/status",
        json={"status": "closed"},
        headers=headers,
    )

    assert create_response.status_code == 403
    assert update_response.status_code == 403
    assert status_response.status_code == 403


def test_platform_admin_lists_tickets_globally(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Administrador global consulta chamados de organizações distintas."""

    first_scope = create_scope(client, test_settings)
    first_ticket = create_ticket_as_platform(client, first_scope)
    second_scope = create_scope(
        client,
        test_settings,
        name="Segunda Organização Chamados",
        code="SEGUNDA-ORG",
        client_payload=ACTIVE_SECOND_CLIENT,
    )
    second_ticket = create_ticket_as_platform(client, second_scope)
    platform_headers = first_scope["platform_headers"]
    assert isinstance(platform_headers, Mapping)

    response = client.get(TICKETS_URL, headers=platform_headers)

    assert response.status_code == 200
    assert {item["id"] for item in response.json()} == {
        first_ticket["id"],
        second_ticket["id"],
    }


def test_organization_admin_cannot_cross_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Administrador organizacional não acessa outra organização."""

    first_scope = create_scope(client, test_settings)
    user = create_scoped_user(client, first_scope, "organization_admin")
    headers = authorization_headers(test_settings, user)
    second_scope = create_scope(
        client,
        test_settings,
        name="Organização Externa",
        code="ORG-EXTERNA",
        client_payload=ACTIVE_SECOND_CLIENT,
    )
    external_ticket = create_ticket_as_platform(client, second_scope)

    get_response = client.get(
        f"{TICKETS_URL}/{external_ticket['id']}",
        headers=headers,
    )
    organization = second_scope["organization"]
    assert isinstance(organization, dict)
    list_response = client.get(
        TICKETS_URL,
        params={"organization_id": organization["id"]},
        headers=headers,
    )

    assert get_response.status_code == 403
    assert list_response.status_code == 403


def test_tenant_admin_cannot_cross_tenant(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Administrador de tenant não acessa outro tenant da organização."""

    scope = create_scope(client, test_settings)
    user = create_scoped_user(client, scope, "tenant_admin")
    headers = authorization_headers(test_settings, user)
    organization = scope["organization"]
    platform_headers = scope["platform_headers"]
    assert isinstance(organization, dict)
    assert isinstance(platform_headers, Mapping)

    other_tenant = create_tenant(
        client,
        str(organization["id"]),
        name="Tenant Secundário",
    )
    other_environment = create_environment(
        client,
        str(other_tenant["id"]),
        name="Ambiente Secundário",
    )
    other_client = create_client(
        client,
        ACTIVE_SECOND_CLIENT,
        str(other_environment["id"]),
        platform_headers,
    )
    response = client.post(
        TICKETS_URL,
        json={
            "environment_id": other_environment["id"],
            "client_id": other_client["id"],
            "title": "Outro tenant",
            "description": "Operação fora do escopo.",
        },
        headers=headers,
    )

    assert response.status_code == 403


@pytest.mark.parametrize("role", ["manager", "analyst", "viewer"])
def test_environment_roles_cannot_cross_environment(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Papéis ambientais não acessam outro ambiente do tenant."""

    scope = create_scope(client, test_settings)
    user = create_scoped_user(client, scope, role)
    headers = authorization_headers(test_settings, user)
    tenant = scope["tenant"]
    platform_headers = scope["platform_headers"]
    assert isinstance(tenant, dict)
    assert isinstance(platform_headers, Mapping)

    other_environment = create_environment(
        client,
        str(tenant["id"]),
        name="Homologação",
    )
    other_client = create_client(
        client,
        ACTIVE_SECOND_CLIENT,
        str(other_environment["id"]),
        platform_headers,
    )
    platform_response = client.post(
        TICKETS_URL,
        json={
            "environment_id": other_environment["id"],
            "client_id": other_client["id"],
            "title": "Outro ambiente",
            "description": "Chamado fora do ambiente do usuário.",
        },
        headers=platform_headers,
    )
    assert platform_response.status_code == 201

    response = client.get(
        f"{TICKETS_URL}/{platform_response.json()['id']}",
        headers=headers,
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role",
    [
        "organization_admin",
        "tenant_admin",
        "manager",
        "analyst",
        "viewer",
    ],
)
def test_limited_roles_cannot_expand_scope_with_filters(
    client: TestClient,
    test_settings: Settings,
    role: str,
) -> None:
    """Filtros explícitos não ampliam o alcance da identidade."""

    scope = create_scope(client, test_settings)
    user = create_scoped_user(client, scope, role)
    headers = authorization_headers(test_settings, user)

    response = client.get(
        TICKETS_URL,
        params={"organization_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers,
    )

    assert response.status_code == 403


def test_chamados_module_must_be_enabled_for_organization(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Usuário organizacional depende da liberação comercial do módulo."""

    scope = create_scope(
        client,
        test_settings,
        enabled_modules={"indicators"},
    )
    user = create_scoped_user(client, scope, "organization_admin")
    headers = authorization_headers(test_settings, user)

    response = client.get(TICKETS_URL, headers=headers)

    assert response.status_code == 403
    assert response.json()["error"] == "module_not_enabled"