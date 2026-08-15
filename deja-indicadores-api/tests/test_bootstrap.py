import subprocess
import sys

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.bootstrap import (
    InitialPlatformAdminAlreadyExistsError,
    PasswordConfirmationMismatchError,
    create_initial_platform_admin,
)
from deja_indicadores_api.core.security import PasswordService
from deja_indicadores_api.user_management.models import (
    UserModel,
    UserRole,
    UserStatus,
)


def test_bootstrap_registers_related_models_in_isolated_process() -> None:
    """Carrega todas as tabelas exigidas pelas chaves estrangeiras."""

    command = (
        "import deja_indicadores_api.bootstrap; "
        "from deja_indicadores_api.core.database import Base; "
        "required={'organizations','tenants','environments','users'}; "
        "missing=required.difference(Base.metadata.tables); "
        "assert not missing, f'Modelos ausentes: {sorted(missing)}'"
    )

    result = subprocess.run(
        [sys.executable, "-c", command],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_create_initial_platform_admin(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Cria o administrador global com senha protegida."""

    with test_session_factory() as session:
        administrator = create_initial_platform_admin(
            session,
            name="  Administrador da Plataforma  ",
            email="  ADMIN@EXAMPLE.COM  ",
            password="senha-segura-123",
            password_confirmation="senha-segura-123",
        )

        assert administrator.name == "Administrador da Plataforma"
        assert administrator.email == "admin@example.com"
        assert administrator.role == UserRole.PLATFORM_ADMIN
        assert administrator.status == UserStatus.ACTIVE
        assert administrator.organization_id is None
        assert administrator.tenant_id is None
        assert administrator.environment_id is None
        assert administrator.password_hash is not None
        assert administrator.password_hash != "senha-segura-123"
        assert PasswordService().verify(
            "senha-segura-123",
            administrator.password_hash,
        )


def test_rejects_second_initial_platform_admin(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Impede a repetição do provisionamento inicial."""

    with test_session_factory() as session:
        create_initial_platform_admin(
            session,
            name="Primeiro Administrador",
            email="primeiro@example.com",
            password="senha-segura-123",
            password_confirmation="senha-segura-123",
        )

        with pytest.raises(
            InitialPlatformAdminAlreadyExistsError,
            match="já foi provisionado",
        ):
            create_initial_platform_admin(
                session,
                name="Segundo Administrador",
                email="segundo@example.com",
                password="outra-senha-456",
                password_confirmation="outra-senha-456",
            )

        user_count = session.scalar(
            select(func.count()).select_from(UserModel)
        )

        assert user_count == 1


def test_rejects_password_confirmation_mismatch(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Impede a criação quando a confirmação diverge."""

    with test_session_factory() as session:
        with pytest.raises(
            PasswordConfirmationMismatchError,
            match="não coincidem",
        ):
            create_initial_platform_admin(
                session,
                name="Administrador",
                email="admin@example.com",
                password="senha-segura-123",
                password_confirmation="senha-diferente-456",
            )

        user_count = session.scalar(
            select(func.count()).select_from(UserModel)
        )

        assert user_count == 0


def test_validates_initial_platform_admin_input(
    test_session_factory: sessionmaker[Session],
) -> None:
    """Aplica as mesmas validações usadas pela administração de usuários."""

    with test_session_factory() as session:
        with pytest.raises(ValidationError):
            create_initial_platform_admin(
                session,
                name=" ",
                email="email-invalido",
                password="curta",
                password_confirmation="curta",
            )

        user_count = session.scalar(
            select(func.count()).select_from(UserModel)
        )

        assert user_count == 0