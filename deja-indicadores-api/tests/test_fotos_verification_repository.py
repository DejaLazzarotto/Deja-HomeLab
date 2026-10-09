"""Testes do repositorio de verificacao do Fotos."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationCodeModel,
)
from deja_indicadores_api.fotos.authentication.repository import (
    FotosVerificationCodeRepository,
)


def test_add_verification_without_commit():
    """Registra verificacao sem confirmar a transacao."""

    session = MagicMock()
    repository = FotosVerificationCodeRepository(session)

    verification = FotosVerificationCodeModel(
        id="verification-test-id",
        user_id="user-test-id",
        purpose="activation",
        code_hash="hash-de-teste",
    )

    result = repository.add(verification)

    assert result is verification

    session.add.assert_called_once_with(verification)
    session.flush.assert_called_once()
    session.commit.assert_not_called()

def test_increment_verification_attempts():
    """Incrementa o contador sem confirmar a transacao."""

    session = MagicMock()
    repository = FotosVerificationCodeRepository(session)

    verification = FotosVerificationCodeModel(
        id="verification-test-id",
        user_id="user-test-id",
        purpose="activation",
        code_hash="hash-de-teste",
        attempts=2,
    )

    repository.increment_attempts(verification)

    assert verification.attempts == 3
    session.flush.assert_called_once()
    session.commit.assert_not_called()




def test_invalidate_active_verification_codes():
    """Invalida codigos anteriores sem confirmar a transacao."""

    session = MagicMock()
    repository = FotosVerificationCodeRepository(session)

    invalidated_at = datetime.now(UTC).replace(tzinfo=None)

    repository.invalidate_active(
        user_id="user-test-id",
        purpose="activation",
        invalidated_at=invalidated_at,
    )

    session.execute.assert_called_once()
    session.flush.assert_called_once()
    session.commit.assert_not_called()

    statement = session.execute.call_args.args[0]

    assert statement.table.name == "fotos_verification_codes"

def test_consume_verification_code():
    """Marca um codigo como utilizado sem confirmar a transacao."""

    session = MagicMock()
    repository = FotosVerificationCodeRepository(session)

    verification = FotosVerificationCodeModel(
        id="verification-test-id",
        user_id="user-test-id",
        purpose="activation",
        code_hash="hash-de-teste",
        attempts=0,
        consumed_at=None,
    )

    consumed_at = datetime.now(UTC).replace(tzinfo=None)

    repository.consume(
        verification,
        consumed_at,
    )

    assert verification.consumed_at == consumed_at
    session.flush.assert_called_once()
    session.commit.assert_not_called()

def test_find_latest_verification_with_lock():
    """Consulta o codigo mais recente com bloqueio opcional."""

    session = MagicMock()

    verification = FotosVerificationCodeModel(
        id="verification-test-id",
        user_id="user-test-id",
        purpose="activation",
        code_hash="hash-de-teste",
    )

    session.scalar.return_value = verification

    repository = FotosVerificationCodeRepository(session)

    result = repository.find_latest(
        user_id="user-test-id",
        purpose="activation",
        for_update=True,
    )

    assert result is verification

    session.scalar.assert_called_once()

    statement = session.scalar.call_args.args[0]

    assert statement._for_update_arg is not None

    session.commit.assert_not_called()

def test_lock_user_uses_for_update():
    """Confirma o bloqueio do usuario durante a transacao."""

    from unittest.mock import MagicMock

    from sqlalchemy.dialects import mysql

    from deja_indicadores_api.fotos.authentication.repository import (
        FotosVerificationCodeRepository,
    )
    from deja_indicadores_api.user_management.models import UserModel

    session = MagicMock()
    user = MagicMock(spec=UserModel)
    session.scalar.return_value = user

    repository = FotosVerificationCodeRepository(session)

    result = repository.lock_user("usuario-001")

    assert result is user
    session.scalar.assert_called_once()

    statement = session.scalar.call_args.args[0]

    sql = str(
        statement.compile(
            dialect=mysql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "FOR UPDATE" in sql.upper()
    assert "usuario-001" in sql