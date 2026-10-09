"""Testes da identificacao de usuarios do Fotos PWA."""

from types import SimpleNamespace
from unittest.mock import Mock

from deja_indicadores_api.fotos.authentication.identity import (
    FotosVerificationIdentityService,
)


def build_identity_service():
    """Prepara o servico com repositorios simulados."""

    service = FotosVerificationIdentityService(Mock())
    service._organization_repository = Mock()
    service._user_repository = Mock()

    return service


def test_identity_finds_user_in_organization():
    """Localiza o usuario pelo codigo e e-mail."""

    service = build_identity_service()

    organization = SimpleNamespace(id="organizacao-001")
    user = SimpleNamespace(id="usuario-001")

    service._organization_repository.find_by_code.return_value = organization
    service._user_repository.find_by_organization_and_email.return_value = user

    result = service.find_user(
        organization_code="cliente-a",
        email="usuario@exemplo.com",
    )

    assert result is user

    service._organization_repository.find_by_code.assert_called_once_with("cliente-a")
    service._user_repository.find_by_organization_and_email.assert_called_once_with(
        "organizacao-001",
        "usuario@exemplo.com",
    )


def test_identity_rejects_unknown_organization():
    """Nao procura usuarios quando a organizacao nao existe."""

    service = build_identity_service()

    service._organization_repository.find_by_code.return_value = None

    result = service.find_user(
        organization_code="inexistente",
        email="usuario@exemplo.com",
    )

    assert result is None
    service._user_repository.find_by_organization_and_email.assert_not_called()


def test_identity_rejects_unknown_email():
    """Retorna None quando o e-mail nao pertence a organizacao."""

    service = build_identity_service()

    service._organization_repository.find_by_code.return_value = SimpleNamespace(
        id="organizacao-001"
    )
    service._user_repository.find_by_organization_and_email.return_value = None

    result = service.find_user(
        organization_code="cliente-a",
        email="desconhecido@exemplo.com",
    )

    assert result is None

    service._user_repository.find_by_organization_and_email.assert_called_once_with(
        "organizacao-001",
        "desconhecido@exemplo.com",
    )


def test_identity_preserves_organization_scope():
    """Nao mistura contas de organizacoes diferentes."""

    service = build_identity_service()

    organizations = {
        "cliente-a": SimpleNamespace(id="organizacao-001"),
        "cliente-b": SimpleNamespace(id="organizacao-002"),
    }

    users = {
        "organizacao-001": SimpleNamespace(id="usuario-001"),
        "organizacao-002": SimpleNamespace(id="usuario-002"),
    }

    service._organization_repository.find_by_code.side_effect = lambda code: organizations.get(code)

    service._user_repository.find_by_organization_and_email.side_effect = (
        lambda organization_id, email: (
            users.get(organization_id) if email == "mesmo@exemplo.com" else None
        )
    )

    first = service.find_user(
        organization_code="cliente-a",
        email="mesmo@exemplo.com",
    )

    second = service.find_user(
        organization_code="cliente-b",
        email="mesmo@exemplo.com",
    )

    assert first.id == "usuario-001"
    assert second.id == "usuario-002"
