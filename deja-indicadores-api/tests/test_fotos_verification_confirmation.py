"""Testes da confirmacao de codigos do Fotos PWA."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

from deja_indicadores_api.fotos.authentication.confirmation import (
    FotosVerificationConfirmationService,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)


def test_confirm_valid_code_updates_password_and_consumes_code():
    """Atualiza a senha e consome o codigo em uma transacao."""

    now = datetime(2026, 10, 9, 12, 0, 0)

    session = Mock()
    code_service = Mock()
    password_service = Mock()

    code_service.utc_now.return_value = now
    code_service.is_usable.return_value = True
    code_service.verify_code.return_value = True

    password_service.hash.return_value = "hash-da-nova-senha"

    service = FotosVerificationConfirmationService(
        session,
        code_service,
        password_service,
    )

    service._repository = Mock()
    service._eligibility = Mock()

    user = SimpleNamespace(
        id="usuario-001",
        password_hash=None,
    )

    verification = SimpleNamespace(
        id="verificacao-001",
        code_hash="a" * 64,
        delivery_status="sent",
        expires_at=now + timedelta(minutes=10),
        attempts=0,
        consumed_at=None,
    )

    service._repository.lock_user.return_value = user
    service._repository.find_latest.return_value = verification
    service._eligibility.can_request.return_value = True

    service.confirm(
        user_id="usuario-001",
        purpose=FotosVerificationPurpose.ACTIVATION,
        code="012345",
        new_password="NovaSenha123",
    )

    service._repository.lock_user.assert_called_once_with("usuario-001")

    service._repository.find_latest.assert_called_once_with(
        "usuario-001",
        "activation",
        for_update=True,
    )

    code_service.is_usable.assert_called_once_with(
        expires_at=verification.expires_at,
        attempts=0,
        consumed_at=None,
        now=now,
    )

    code_service.verify_code.assert_called_once_with(
        verification_id="verificacao-001",
        user_id="usuario-001",
        purpose="activation",
        code="012345",
        expected_hash="a" * 64,
    )

    password_service.hash.assert_called_once_with("NovaSenha123")

    assert user.password_hash == "hash-da-nova-senha"

    service._repository.consume.assert_called_once_with(
        verification,
        now,
    )

    service._repository.increment_attempts.assert_not_called()

    session.commit.assert_called_once()
    session.rollback.assert_not_called()


def test_confirm_invalid_code_records_attempt():
    """Registra tentativa incorreta sem alterar a senha."""

    import pytest

    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationInvalidCodeError,
    )

    now = datetime(2026, 10, 9, 12, 0, 0)

    session = Mock()
    code_service = Mock()
    password_service = Mock()

    code_service.utc_now.return_value = now
    code_service.is_usable.return_value = True
    code_service.verify_code.return_value = False

    service = FotosVerificationConfirmationService(
        session,
        code_service,
        password_service,
    )

    service._repository = Mock()
    service._eligibility = Mock()

    user = SimpleNamespace(
        id="usuario-001",
        password_hash=None,
    )

    verification = SimpleNamespace(
        id="verificacao-001",
        code_hash="a" * 64,
        delivery_status="sent",
        expires_at=now + timedelta(minutes=10),
        attempts=0,
        consumed_at=None,
    )

    service._repository.lock_user.return_value = user
    service._repository.find_latest.return_value = verification
    service._eligibility.can_request.return_value = True

    with pytest.raises(FotosVerificationInvalidCodeError):
        service.confirm(
            user_id="usuario-001",
            purpose=FotosVerificationPurpose.ACTIVATION,
            code="999999",
            new_password="NovaSenha123",
        )

    service._repository.increment_attempts.assert_called_once_with(
        verification,
    )

    assert user.password_hash is None

    password_service.hash.assert_not_called()
    service._repository.consume.assert_not_called()

    session.commit.assert_called_once()
    session.rollback.assert_called_once()


def test_confirm_rejects_exhausted_attempts():
    """Rejeita codigo que atingiu cinco tentativas."""

    import pytest

    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationInvalidCodeError,
    )

    now = datetime(2026, 10, 9, 12, 0, 0)

    session = Mock()
    code_service = Mock()
    password_service = Mock()

    code_service.utc_now.return_value = now
    code_service.is_usable.return_value = False

    service = FotosVerificationConfirmationService(
        session,
        code_service,
        password_service,
    )

    service._repository = Mock()
    service._eligibility = Mock()

    user = SimpleNamespace(
        id="usuario-001",
        password_hash=None,
    )

    verification = SimpleNamespace(
        id="verificacao-001",
        code_hash="a" * 64,
        delivery_status="sent",
        expires_at=now + timedelta(minutes=10),
        attempts=5,
        consumed_at=None,
    )

    service._repository.lock_user.return_value = user
    service._repository.find_latest.return_value = verification
    service._eligibility.can_request.return_value = True

    with pytest.raises(FotosVerificationInvalidCodeError):
        service.confirm(
            user_id="usuario-001",
            purpose=FotosVerificationPurpose.ACTIVATION,
            code="012345",
            new_password="NovaSenha123",
        )

    code_service.is_usable.assert_called_once_with(
        expires_at=verification.expires_at,
        attempts=5,
        consumed_at=None,
        now=now,
    )

    code_service.verify_code.assert_not_called()
    password_service.hash.assert_not_called()

    service._repository.increment_attempts.assert_not_called()
    service._repository.consume.assert_not_called()

    assert user.password_hash is None

    session.commit.assert_not_called()
    session.rollback.assert_called_once()


def test_confirm_rejects_expired_or_consumed_code():
    """Rejeita codigos expirados ou ja consumidos."""

    import pytest

    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationInvalidCodeError,
    )

    now = datetime(2026, 10, 9, 12, 0, 0)

    for expires_at, consumed_at in (
        (now - timedelta(seconds=1), None),
        (now + timedelta(minutes=10), now),
    ):
        session = Mock()
        code_service = Mock()
        password_service = Mock()

        code_service.utc_now.return_value = now
        code_service.is_usable.return_value = False

        service = FotosVerificationConfirmationService(
            session,
            code_service,
            password_service,
        )

        service._repository = Mock()
        service._eligibility = Mock()

        user = SimpleNamespace(
            id="usuario-001",
            password_hash=None,
        )

        verification = SimpleNamespace(
            id="verificacao-001",
            code_hash="a" * 64,
            delivery_status="sent",
            expires_at=expires_at,
            attempts=0,
            consumed_at=consumed_at,
        )

        service._repository.lock_user.return_value = user
        service._repository.find_latest.return_value = verification
        service._eligibility.can_request.return_value = True

        with pytest.raises(FotosVerificationInvalidCodeError):
            service.confirm(
                user_id="usuario-001",
                purpose=FotosVerificationPurpose.ACTIVATION,
                code="012345",
                new_password="NovaSenha123",
            )

        code_service.is_usable.assert_called_once_with(
            expires_at=expires_at,
            attempts=0,
            consumed_at=consumed_at,
            now=now,
        )

        code_service.verify_code.assert_not_called()
        password_service.hash.assert_not_called()

        service._repository.increment_attempts.assert_not_called()
        service._repository.consume.assert_not_called()

        assert user.password_hash is None

        session.commit.assert_not_called()
        session.rollback.assert_called_once()


def test_confirm_rejects_code_not_delivered():
    """Rejeita codigos pendentes ou com falha de envio."""

    import pytest

    from deja_indicadores_api.fotos.authentication.confirmation import (
        FotosVerificationInvalidCodeError,
    )

    now = datetime(2026, 10, 9, 12, 0, 0)

    for delivery_status in ("pending", "failed"):
        session = Mock()
        code_service = Mock()
        password_service = Mock()

        code_service.utc_now.return_value = now
        code_service.is_usable.return_value = True
        code_service.verify_code.return_value = True

        service = FotosVerificationConfirmationService(
            session,
            code_service,
            password_service,
        )

        service._repository = Mock()
        service._eligibility = Mock()

        user = SimpleNamespace(
            id="usuario-001",
            password_hash=None,
        )

        verification = SimpleNamespace(
            id="verificacao-001",
            code_hash="a" * 64,
            delivery_status=delivery_status,
            expires_at=now + timedelta(minutes=10),
            attempts=0,
            consumed_at=None,
        )

        service._repository.lock_user.return_value = user
        service._repository.find_latest.return_value = verification
        service._eligibility.can_request.return_value = True

        with pytest.raises(FotosVerificationInvalidCodeError):
            service.confirm(
                user_id="usuario-001",
                purpose=FotosVerificationPurpose.ACTIVATION,
                code="012345",
                new_password="NovaSenha123",
            )

        code_service.is_usable.assert_not_called()
        code_service.verify_code.assert_not_called()
        password_service.hash.assert_not_called()

        service._repository.increment_attempts.assert_not_called()
        service._repository.consume.assert_not_called()

        assert user.password_hash is None
        assert verification.attempts == 0
        assert verification.consumed_at is None

        session.commit.assert_not_called()
        session.rollback.assert_called_once()
