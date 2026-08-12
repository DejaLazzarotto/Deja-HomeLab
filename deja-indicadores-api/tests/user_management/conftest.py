from collections.abc import Callable, Generator

import pytest
from fastapi import FastAPI

from deja_indicadores_api.authentication.dependencies import (
    get_current_user,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.user_management.models import UserRole

CurrentOrganizationSetter = Callable[[str], None]


@pytest.fixture(autouse=True)
def authorize_user_management_requests(
    test_app: FastAPI,
) -> Generator[None, None, None]:
    """Fornece identidade administrativa aos testes de domínio."""

    current_user = AuthenticatedUser(
        id="11111111-1111-1111-1111-111111111111",
        organization_id=None,
        tenant_id=None,
        environment_id=None,
        name="Administrador dos Testes",
        email="admin.testes@deja.com",
        role=UserRole.PLATFORM_ADMIN,
    )

    def override_get_current_user() -> AuthenticatedUser:
        return current_user

    def set_platform_administrator() -> None:
        current_user.organization_id = None
        current_user.tenant_id = None
        current_user.environment_id = None
        current_user.role = UserRole.PLATFORM_ADMIN

    def set_current_organization(organization_id: str) -> None:
        current_user.organization_id = organization_id
        current_user.tenant_id = None
        current_user.environment_id = None
        current_user.role = UserRole.ORGANIZATION_ADMIN

    test_app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )
    test_app.state.set_platform_test_administrator = (
        set_platform_administrator
    )
    test_app.state.set_current_test_organization = (
        set_current_organization
    )

    try:
        yield
    finally:
        test_app.dependency_overrides.pop(get_current_user, None)
        del test_app.state.set_platform_test_administrator
        del test_app.state.set_current_test_organization