from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.module_management.models import (
    OrganizationModuleModel,
)
from deja_indicadores_api.user_management.models import (
    UserModuleAccessModel,
    UserModuleRole,
)
from tests.authentication.test_authentication_api import (
    LOGIN_URL,
    create_environment,
    create_organization,
    create_tenant,
    create_user,
    set_password,
)

ME_URL = "/api/v1/auth/me"


def create_signed_token(
    settings: Settings,
    user: dict[str, object],
    *,
    expires_at: datetime | None = None,
    token_type: str = "access",
    secret_key: str | None = None,
    remove_claim: str | None = None,
    organization_id: str | None = None,
) -> str:
    """Cria um JWT controlado para os cenários de validação."""

    issued_at = datetime.now(UTC)
    payload: dict[str, object] = {
        "sub": user["id"],
        "organization_id": (
            organization_id if organization_id is not None else user["organization_id"]
        ),
        "tenant_id": user["tenant_id"],
        "environment_id": user["environment_id"],
        "role": user["role"],
        "type": token_type,
        "iat": issued_at,
        "exp": expires_at or issued_at + timedelta(minutes=15),
        "jti": str(uuid4()),
    }

    if remove_claim is not None:
        payload.pop(remove_claim)

    return jwt.encode(
        payload,
        secret_key or settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def assert_invalid_access_token(response: object) -> None:
    """Valida o contrato público de rejeição do Bearer token."""

    assert hasattr(response, "status_code")
    assert response.status_code == 401
    assert response.json() == {
        "error": "invalid_access_token",
        "message": "Token de acesso inválido.",
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_returns_authenticated_user_and_institutional_scope(
    client: TestClient,
) -> None:
    """Retorna a identidade persistida associada ao token válido."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="identidade@deja.com",
        role="analyst",
    )
    set_password(client, str(user["id"]))

    login_response = client.post(
        LOGIN_URL,
        json={
            "organization_code": organization["code"],
            "email": "identidade@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert login_response.status_code == 200

    response = client.get(
        ME_URL,
        headers={
            "Authorization": (f"Bearer {login_response.json()['access_token']}"),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
    "id": user["id"],
    "organization_id": organization["id"],
    "tenant_id": tenant["id"],
    "environment_id": environment["id"],
    "name": "Usuário Principal",
    "email": "identidade@deja.com",
    "role": "analyst",
    "enabled_modules": [
        "chamados",
        "fotos",
        "indicators",
        "measurements",
        "reports",
    ],
    "module_access": [],
}

def test_me_rejects_missing_bearer_token(
    client: TestClient,
) -> None:
    """Rejeita requisição sem cabeçalho Authorization."""

    response = client.get(ME_URL)

    assert_invalid_access_token(response)


def test_me_rejects_malformed_bearer_token(
    client: TestClient,
) -> None:
    """Rejeita conteúdo que não representa um JWT."""

    response = client.get(
        ME_URL,
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert_invalid_access_token(response)


def test_me_rejects_token_with_tampered_signature(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita token assinado por uma chave diferente."""

    organization = create_organization(client)
    user = create_user(client, str(organization["id"]))
    token = create_signed_token(
        test_settings,
        user,
        secret_key="chave-adulterada-que-nao-e-a-chave-da-aplicacao",
    )

    response = client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert_invalid_access_token(response)


def test_me_rejects_expired_token(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita token cuja expiração já ocorreu."""

    organization = create_organization(client)
    user = create_user(client, str(organization["id"]))
    token = create_signed_token(
        test_settings,
        user,
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
    )

    response = client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert_invalid_access_token(response)


def test_me_rejects_token_with_non_access_type(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita JWT válido que não seja um token de acesso."""

    organization = create_organization(client)
    user = create_user(client, str(organization["id"]))
    token = create_signed_token(
        test_settings,
        user,
        token_type="refresh",
    )

    response = client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert_invalid_access_token(response)


def test_me_rejects_token_without_required_claim(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita token sem uma claim obrigatória."""

    organization = create_organization(client)
    user = create_user(client, str(organization["id"]))
    token = create_signed_token(
        test_settings,
        user,
        remove_claim="role",
    )

    response = client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert_invalid_access_token(response)


def test_me_rejects_token_for_nonexistent_user(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita token válido associado a usuário inexistente."""

    organization = create_organization(client)
    user = create_user(client, str(organization["id"]))
    user["id"] = "00000000-0000-0000-0000-000000000000"
    token = create_signed_token(test_settings, user)

    response = client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert_invalid_access_token(response)


def test_me_rejects_token_for_inactive_user(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita token válido associado a usuário inativo."""

    organization = create_organization(client)
    user = create_user(
        client,
        str(organization["id"]),
        email="inativo.token@deja.com",
        status="inactive",
    )
    token = create_signed_token(test_settings, user)

    response = client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert_invalid_access_token(response)


def test_me_rejects_token_with_divergent_institutional_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Rejeita claims institucionais diferentes do cadastro atual."""

    organization = create_organization(client)
    user = create_user(client, str(organization["id"]))
    token = create_signed_token(
        test_settings,
        user,
        organization_id="00000000-0000-0000-0000-000000000000",
    )

    response = client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert_invalid_access_token(response)

def test_me_returns_persisted_module_access(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Retorna os acessos funcionais persistidos para o usuário."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )
    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="modulos@deja.com",
        role="analyst",
    )
    set_password(
        client,
        str(user["id"]),
    )

    with test_session_factory() as session:
        session.add_all(
            [
                UserModuleAccessModel(
                    user_id=str(user["id"]),
                    module_key="fotos",
                    role=UserModuleRole.MANAGER,
                ),
                UserModuleAccessModel(
                    user_id=str(user["id"]),
                    module_key="reports",
                    role=UserModuleRole.VIEWER,
                ),
            ]
        )
        session.commit()

    login_response = client.post(
        LOGIN_URL,
        json={
            "organization_code": organization["code"],
            "email": "modulos@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert login_response.status_code == 200

    response = client.get(
        ME_URL,
        headers={
            "Authorization": (
                f"Bearer {login_response.json()['access_token']}"
            ),
        },
    )

    assert response.status_code == 200
    assert response.json()["module_access"] == [
        {
            "module_key": "fotos",
            "role": "manager",
        },
        {
            "module_key": "reports",
            "role": "viewer",
        },
    ]


def test_me_reflects_module_access_change_without_new_token(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Aplica mudanças de acesso na requisição seguinte."""

    organization = create_organization(client)
    tenant = create_tenant(
        client,
        str(organization["id"]),
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )
    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="acesso.dinamico@deja.com",
        role="viewer",
    )
    set_password(
        client,
        str(user["id"]),
    )

    with test_session_factory() as session:
        session.add(
            UserModuleAccessModel(
                user_id=str(user["id"]),
                module_key="fotos",
                role=UserModuleRole.VIEWER,
            )
        )
        session.commit()

    login_response = client.post(
        LOGIN_URL,
        json={
            "organization_code": organization["code"],
            "email": "acesso.dinamico@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_response = client.get(
        ME_URL,
        headers=headers,
    )

    assert first_response.status_code == 200
    assert first_response.json()["module_access"] == [
        {
            "module_key": "fotos",
            "role": "viewer",
        }
    ]

    with test_session_factory() as session:
        access = session.get(
            UserModuleAccessModel,
            (
                str(user["id"]),
                "fotos",
            ),
        )

        assert access is not None

        access.role = UserModuleRole.MANAGER
        session.commit()

    second_response = client.get(
        ME_URL,
        headers=headers,
    )

    assert second_response.status_code == 200
    assert second_response.json()["module_access"] == [
        {
            "module_key": "fotos",
            "role": "manager",
        }
    ]


def test_me_omits_access_to_disabled_organization_module(
    client: TestClient,
    test_session_factory: sessionmaker[Session],
) -> None:
    """Oculta acesso individual quando o módulo é desabilitado."""

    organization = create_organization(client)
    organization_id = str(organization["id"])
    tenant = create_tenant(
        client,
        organization_id,
    )
    environment = create_environment(
        client,
        str(tenant["id"]),
    )
    user = create_user(
        client,
        organization_id,
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="modulo.desabilitado@deja.com",
        role="viewer",
    )
    set_password(
        client,
        str(user["id"]),
    )

    with test_session_factory() as session:
        session.add(
            UserModuleAccessModel(
                user_id=str(user["id"]),
                module_key="fotos",
                role=UserModuleRole.VIEWER,
            )
        )
        session.commit()

    login_response = client.post(
        LOGIN_URL,
        json={
            "organization_code": organization["code"],
            "email": "modulo.desabilitado@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_response = client.get(
        ME_URL,
        headers=headers,
    )

    assert first_response.status_code == 200
    assert first_response.json()["module_access"] == [
        {
            "module_key": "fotos",
            "role": "viewer",
        }
    ]

    with test_session_factory() as session:
        association = session.get(
            OrganizationModuleModel,
            (
                organization_id,
                "fotos",
            ),
        )

        assert association is not None

        association.enabled = False
        session.commit()

    second_response = client.get(
        ME_URL,
        headers=headers,
    )

    assert second_response.status_code == 200
    assert "fotos" not in second_response.json()["enabled_modules"]
    assert second_response.json()["module_access"] == []