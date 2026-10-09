"""Testes das regras de elegibilidade do Fotos PWA."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from deja_indicadores_api.fotos.authentication.eligibility import (
    FotosVerificationEligibility,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)
from deja_indicadores_api.tenant_management.models import (
    TenantManagementStatus,
)
from deja_indicadores_api.user_management.models import (
    UserModuleRole,
    UserStatus,
)


def build_eligibility(
    *,
    status=UserStatus.ACTIVE,
    organization_id="organizacao-001",
    role=UserModuleRole.VIEWER,
    module_enabled=True,
    organization_status=TenantManagementStatus.ACTIVE,
    password_hash=None,
):
    """Prepara usuario e repositorios simulados."""

    user = SimpleNamespace(
        id="usuario-001",
        organization_id=organization_id,
        status=status,
        password_hash=password_hash,
    )

    module_access_repository = Mock()
    organization_module_repository = Mock()
    organization_repository = Mock()
    organization_repository.find_by_id.return_value = SimpleNamespace(
        status=organization_status,
    )

    module_access_repository.find.return_value = (
        SimpleNamespace(role=role)
        if role is not None
        else None
    )

    organization_module_repository.is_enabled.return_value = (
        module_enabled
    )

    eligibility = FotosVerificationEligibility(
        module_access_repository,
        organization_module_repository,
    organization_repository,
    )

    return eligibility, user


@pytest.mark.parametrize(
    "role",
    [
        UserModuleRole.VIEWER,
        UserModuleRole.MANAGER,
    ],
)
def test_activation_allowed_for_fotos_user_without_password(role):
    """Permite ativacao para usuario habilitado sem senha."""

    eligibility, user = build_eligibility(role=role)

    assert eligibility.can_request(
        user=user,
        purpose=FotosVerificationPurpose.ACTIVATION,
    )


def test_password_reset_allowed_for_user_with_password():
    """Permite recuperacao quando a senha ja existe."""

    eligibility, user = build_eligibility(
        password_hash="hash-existente",
    )

    assert eligibility.can_request(
        user=user,
        purpose=FotosVerificationPurpose.PASSWORD_RESET,
    )


@pytest.mark.parametrize(
    ("purpose", "password_hash"),
    [
        (
            FotosVerificationPurpose.ACTIVATION,
            "hash-existente",
        ),
        (
            FotosVerificationPurpose.PASSWORD_RESET,
            None,
        ),
    ],
)
def test_reject_incompatible_password_state(
    purpose,
    password_hash,
):
    """Rejeita finalidade incompatível com a senha existente."""

    eligibility, user = build_eligibility(
        password_hash=password_hash,
    )

    assert not eligibility.can_request(
        user=user,
        purpose=purpose,
    )


def test_reject_inactive_user():
    """Rejeita usuario inativo."""

    eligibility, user = build_eligibility(
        status=UserStatus.INACTIVE,
    )

    assert not eligibility.can_request(
        user=user,
        purpose=FotosVerificationPurpose.ACTIVATION,
    )


def test_reject_user_without_organization():
    """Rejeita usuario sem organizacao."""

    eligibility, user = build_eligibility(
        organization_id=None,
    )

    assert not eligibility.can_request(
        user=user,
        purpose=FotosVerificationPurpose.ACTIVATION,
    )


def test_reject_disabled_fotos_module():
    """Rejeita usuario cuja organizacao nao habilitou Fotos."""

    eligibility, user = build_eligibility(
        module_enabled=False,
    )

    assert not eligibility.can_request(
        user=user,
        purpose=FotosVerificationPurpose.ACTIVATION,
    )


@pytest.mark.parametrize(
    "role",
    [
        None,
        UserModuleRole.ANALYST,
    ],
)
def test_reject_missing_or_invalid_fotos_access(role):
    """Rejeita ausencia de acesso e papel nao permitido."""

    eligibility, user = build_eligibility(role=role)

    assert not eligibility.can_request(
        user=user,
        purpose=FotosVerificationPurpose.ACTIVATION,
    )


@pytest.mark.parametrize(
    "organization_status",
    [
        TenantManagementStatus.INACTIVE,
        TenantManagementStatus.PROVISIONING,
        None,
    ],
)
@pytest.mark.parametrize(
    "purpose",
    [
        FotosVerificationPurpose.ACTIVATION,
        FotosVerificationPurpose.PASSWORD_RESET,
    ],
)
def test_organization_must_be_active_for_verification(
    organization_status,
    purpose,
):
    """Bloqueia codigos para organizacoes nao ativas ou inexistentes."""

    password_hash = (
        "hash-existente"
        if purpose == FotosVerificationPurpose.PASSWORD_RESET
        else None
    )

    eligibility, user = build_eligibility(
        organization_status=organization_status,
        password_hash=password_hash,
    )

    if organization_status is None:
        eligibility._organization_repository.find_by_id.return_value = None

    assert not eligibility.can_request(
        user=user,
        purpose=purpose,
    )
