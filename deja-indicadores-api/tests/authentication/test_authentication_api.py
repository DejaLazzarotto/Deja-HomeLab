from uuid import uuid4

from fastapi.testclient import TestClient

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.core.security import (
    AccessTokenService,
    PasswordService,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    OrganizationModel,
    TenantManagementStatus,
    TenantModel,
)
from deja_indicadores_api.user_management.models import (
    UserModel,
    UserRole,
    UserStatus,
)

ORGANIZATIONS_URL = "/api/v1/organizations"
TENANTS_URL = "/api/v1/tenants"
ENVIRONMENTS_URL = "/api/v1/environments"
USERS_URL = "/api/v1/users"
LOGIN_URL = "/api/v1/auth/login"


def create_organization(
    client: TestClient,
    name: str = "Organização Principal",
) -> dict[str, object]:
    """Insere uma organização diretamente para os testes."""

    organization = OrganizationModel(
        id=str(uuid4()),
        name=name,
        status=TenantManagementStatus.ACTIVE,
    )
    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add(organization)
        session.commit()
        session.refresh(organization)

    return {
        "id": organization.id,
        "name": organization.name,
        "status": organization.status.value,
    }


def create_tenant(
    client: TestClient,
    organization_id: str,
    *,
    name: str = "Tenant Principal",
) -> dict[str, object]:
    """Insere um tenant diretamente para os testes."""

    tenant = TenantModel(
        id=str(uuid4()),
        organization_id=organization_id,
        name=name,
        status=TenantManagementStatus.ACTIVE,
    )
    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add(tenant)
        session.commit()
        session.refresh(tenant)

    return {
        "id": tenant.id,
        "organization_id": tenant.organization_id,
        "name": tenant.name,
        "status": tenant.status.value,
    }


def create_environment(
    client: TestClient,
    tenant_id: str,
    *,
    name: str = "Produção",
) -> dict[str, object]:
    """Insere um ambiente diretamente para os testes."""

    environment = EnvironmentModel(
        id=str(uuid4()),
        tenant_id=tenant_id,
        name=name,
        status=TenantManagementStatus.ACTIVE,
    )
    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add(environment)
        session.commit()
        session.refresh(environment)

    return {
        "id": environment.id,
        "tenant_id": environment.tenant_id,
        "name": environment.name,
        "status": environment.status.value,
    }


def create_user(
    client: TestClient,
    organization_id: str | None,
    *,
    tenant_id: str | None = None,
    environment_id: str | None = None,
    email: str = "usuario@deja.com",
    role: str = "organization_admin",
    status: str = "active",
) -> dict[str, object]:
    """Insere um usuário diretamente para os testes de autenticação."""

    user = UserModel(
        id=str(uuid4()),
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        name="Usuário Principal",
        email=email,
        password_hash=None,
        role=UserRole(role),
        status=UserStatus(status),
    )

    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    return {
        "id": user.id,
        "organization_id": user.organization_id,
        "tenant_id": user.tenant_id,
        "environment_id": user.environment_id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "status": user.status.value,
    }


def set_password(
    client: TestClient,
    user_id: str,
    password: str = "SenhaSegura123!",
) -> None:
    """Define diretamente a senha do usuário de autenticação."""

    session_factory = client.app.state.test_session_factory

    with session_factory() as session:
        user = session.get(UserModel, user_id)

        assert user is not None

        user.password_hash = PasswordService().hash(password)
        session.commit()


def create_access_token_service(
    settings: Settings,
) -> AccessTokenService:
    """Cria o serviço JWT usando exclusivamente as configurações de teste."""

    return AccessTokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.access_token_expire_minutes,
    )


def test_login_issues_access_token_with_institutional_claims(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Emite token com usuário, organização, tenant, ambiente e papel."""

    organization = create_organization(client)
    tenant = create_tenant(client, str(organization["id"]))
    environment = create_environment(client, str(tenant["id"]))
    user = create_user(
        client,
        str(organization["id"]),
        tenant_id=str(tenant["id"]),
        environment_id=str(environment["id"]),
        email="analista@deja.com",
        role="analyst",
    )
    set_password(client, str(user["id"]))

    response = client.post(
        LOGIN_URL,
        json={
            "organization_id": organization["id"],
            "email": "  ANALISTA@deja.com  ",
            "password": "SenhaSegura123!",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert body["expires_in"] == (
        test_settings.access_token_expire_minutes * 60
    )
    assert body["access_token"]

    payload = create_access_token_service(test_settings).decode(
        body["access_token"]
    )

    assert payload["sub"] == user["id"]
    assert payload["organization_id"] == organization["id"]
    assert payload["tenant_id"] == tenant["id"]
    assert payload["environment_id"] == environment["id"]
    assert payload["role"] == "analyst"
    assert payload["type"] == "access"
    assert payload["jti"]
    assert payload["exp"] > payload["iat"]


def test_login_platform_admin_has_global_null_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Emite token global sem vínculos de cliente."""

    user = create_user(
        client,
        None,
        email="platform.admin@deja.com",
        role="platform_admin",
    )
    set_password(client, str(user["id"]))

    response = client.post(
        LOGIN_URL,
        json={
            "organization_id": None,
            "email": "platform.admin@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert response.status_code == 200

    payload = create_access_token_service(test_settings).decode(
        response.json()["access_token"]
    )

    assert payload["sub"] == user["id"]
    assert payload["organization_id"] is None
    assert payload["tenant_id"] is None
    assert payload["environment_id"] is None
    assert payload["role"] == "platform_admin"


def test_login_organization_admin_has_null_operational_scope(
    client: TestClient,
    test_settings: Settings,
) -> None:
    """Representa escopos opcionais como nulos no token."""

    organization = create_organization(client)
    user = create_user(
        client,
        str(organization["id"]),
        email="admin@deja.com",
    )
    set_password(client, str(user["id"]))

    response = client.post(
        LOGIN_URL,
        json={
            "organization_id": organization["id"],
            "email": "admin@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert response.status_code == 200

    payload = create_access_token_service(test_settings).decode(
        response.json()["access_token"]
    )

    assert payload["tenant_id"] is None
    assert payload["environment_id"] is None
    assert payload["role"] == "organization_admin"


def test_login_rejects_invalid_credentials_without_revealing_field(
    client: TestClient,
) -> None:
    """Usa a mesma resposta para organização, e-mail ou senha incorretos."""

    organization = create_organization(client)
    user = create_user(
        client,
        str(organization["id"]),
        email="usuario@deja.com",
    )
    set_password(client, str(user["id"]))

    invalid_credentials = [
        {
            "organization_id": (
                "00000000-0000-0000-0000-000000000000"
            ),
            "email": "usuario@deja.com",
            "password": "SenhaSegura123!",
        },
        {
            "organization_id": organization["id"],
            "email": "inexistente@deja.com",
            "password": "SenhaSegura123!",
        },
        {
            "organization_id": organization["id"],
            "email": "usuario@deja.com",
            "password": "SenhaIncorreta123!",
        },
    ]

    for credentials in invalid_credentials:
        response = client.post(LOGIN_URL, json=credentials)

        assert response.status_code == 401
        assert response.json() == {
            "error": "invalid_credentials",
            "message": "Organização, e-mail ou senha inválidos.",
        }
        assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_user_without_password(
    client: TestClient,
) -> None:
    """Impede login enquanto uma senha não tiver sido definida."""

    organization = create_organization(client)
    create_user(
        client,
        str(organization["id"]),
        email="sem.senha@deja.com",
    )

    response = client.post(
        LOGIN_URL,
        json={
            "organization_id": organization["id"],
            "email": "sem.senha@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_credentials"
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_inactive_user(
    client: TestClient,
) -> None:
    """Impede a criação de sessão para um usuário inativo."""

    organization = create_organization(client)
    user = create_user(
        client,
        str(organization["id"]),
        email="inativo@deja.com",
        status="inactive",
    )
    set_password(client, str(user["id"]))

    response = client.post(
        LOGIN_URL,
        json={
            "organization_id": organization["id"],
            "email": "inativo@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": "inactive_user",
        "message": "O usuário está inativo.",
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_short_password(
    client: TestClient,
) -> None:
    """Rejeita senha que não atende ao contrato mínimo."""

    organization = create_organization(client)

    response = client.post(
        LOGIN_URL,
        json={
            "organization_id": organization["id"],
            "email": "usuario@deja.com",
            "password": "curta",
        },
    )

    assert response.status_code == 422


def test_login_rejects_invalid_organization_id(
    client: TestClient,
) -> None:
    """Rejeita identificador de organização com tamanho inválido."""

    response = client.post(
        LOGIN_URL,
        json={
            "organization_id": "invalid-id",
            "email": "usuario@deja.com",
            "password": "SenhaSegura123!",
        },
    )

    assert response.status_code == 422


def test_login_rejects_invalid_email(
    client: TestClient,
) -> None:
    """Rejeita endereço de e-mail inválido."""

    response = client.post(
        LOGIN_URL,
        json={
            "organization_id": (
                "00000000-0000-0000-0000-000000000000"
            ),
            "email": "email-invalido",
            "password": "SenhaSegura123!",
        },
    )

    assert response.status_code == 422
