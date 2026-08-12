from collections.abc import Generator

import pytest
from fastapi import FastAPI

from deja_indicadores_api.authentication.dependencies import (
    get_current_user,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.user_management.models import UserRole


@pytest.fixture(autouse=True)
def authorize_tenant_management_requests(
    test_app: FastAPI,
) -> Generator[None, None, None]:
    """Fornece identidade global aos testes de domínio institucional."""

    current_user = AuthenticatedUser(
        id="99999999-9999-9999-9999-999999999999",
        organization_id=None,
        tenant_id=None,
        environment_id=None,
        name="Administrador Global dos Testes",
        email="platform.admin.testes@deja.com",
        role=UserRole.PLATFORM_ADMIN,
    )

    def override_get_current_user() -> AuthenticatedUser:
        return current_user

    test_app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        yield
    finally:
        test_app.dependency_overrides.pop(get_current_user, None)