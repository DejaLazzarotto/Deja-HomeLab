"""Testes da emissao transacional dos codigos do Fotos PWA."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from deja_indicadores_api.fotos.authentication.issuance import (
    FotosVerificationIssuanceService,
    FotosVerificationNotEligibleError,
)
from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationPurpose,
)


def test_issue_creates_verification_and_commits():
    """Emite codigo elegivel e confirma a transacao."""

    now = datetime(2026, 10, 9, 12, 0, 0)
    session = Mock()
    code_service = Mock()

    code_service.utc_now.return_value = now
    code_service.generate_verification_id.return_value = "verificacao-001"
    code_service.generate_code.return_value = "012345"
    code_service.expires_at.return_value = now + timedelta(minutes=10)
    code_service.hash_code.return_value = "a" * 64

    service = FotosVerificationIssuanceService(
        session,
        code_service,
    )

    service._repository = Mock()
    service._eligibility = Mock()

    service._repository.lock_user.return_value = SimpleNamespace(id="usuario-001")
    service._repository.find_latest.return_value = None
    service._eligibility.can_request.return_value = True

    result = service.issue(
        user_id="usuario-001",
        purpose=FotosVerificationPurpose.ACTIVATION,
    )

    assert result.verification_id == "verificacao-001"
    assert result.code == "012345"
    assert result.expires_at == now + timedelta(minutes=10)

    service._repository.lock_user.assert_called_once_with("usuario-001")

    service._repository.find_latest.assert_called_once_with(
        "usuario-001",
        "activation",
        for_update=True,
    )

    service._repository.invalidate_active.assert_called_once_with(
        "usuario-001",
        "activation",
        now,
    )

    service._repository.add.assert_called_once()

    verification = service._repository.add.call_args.args[0]

    assert verification.id == "verificacao-001"
    assert verification.user_id == "usuario-001"
    assert verification.purpose == "activation"
    assert verification.code_hash == "a" * 64
    assert verification.expires_at == now + timedelta(minutes=10)
    assert verification.attempts == 0
    assert verification.consumed_at is None
    assert verification.created_at == now

    code_service.hash_code.assert_called_once_with(
        verification_id="verificacao-001",
        user_id="usuario-001",
        purpose="activation",
        code="012345",
    )

    session.commit.assert_called_once()
    session.rollback.assert_not_called()


@pytest.mark.parametrize(
    "user_exists",
    [False, True],
)
def test_issue_rejects_ineligible_user(user_exists):
    """Rejeita usuario inexistente ou sem elegibilidade."""

    session = Mock()
    code_service = Mock()

    service = FotosVerificationIssuanceService(
        session,
        code_service,
    )

    service._repository = Mock()
    service._eligibility = Mock()

    if user_exists:
        service._repository.lock_user.return_value = SimpleNamespace(id="usuario-001")
        service._eligibility.can_request.return_value = False
    else:
        service._repository.lock_user.return_value = None

    with pytest.raises(FotosVerificationNotEligibleError):
        service.issue(
            user_id="usuario-001",
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    service._repository.lock_user.assert_called_once_with("usuario-001")

    if user_exists:
        service._eligibility.can_request.assert_called_once()
    else:
        service._eligibility.can_request.assert_not_called()

    service._repository.find_latest.assert_not_called()
    service._repository.add.assert_not_called()
    service._repository.invalidate_active.assert_not_called()

    code_service.generate_code.assert_not_called()

    session.commit.assert_not_called()
    session.rollback.assert_called_once()


def test_issue_rejects_cooldown():
    """Impede reenvio antes do intervalo minimo."""

    now = datetime(2026, 10, 9, 12, 0, 0)
    session = Mock()
    code_service = Mock()
    code_service.utc_now.return_value = now
    code_service.can_resend.return_value = False

    service = FotosVerificationIssuanceService(
        session,
        code_service,
    )

    service._repository = Mock()
    service._eligibility = Mock()

    service._repository.lock_user.return_value = SimpleNamespace(id="usuario-001")
    service._eligibility.can_request.return_value = True
    service._repository.find_latest.return_value = SimpleNamespace(
        created_at=now - timedelta(seconds=30),
        delivery_status="sent",
    )

    from deja_indicadores_api.fotos.authentication.issuance import (
        FotosVerificationCooldownError,
    )

    with pytest.raises(FotosVerificationCooldownError):
        service.issue(
            user_id="usuario-001",
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    code_service.can_resend.assert_called_once_with(
        created_at=now - timedelta(seconds=30),
        now=now,
    )
    code_service.generate_code.assert_not_called()

    service._repository.add.assert_not_called()
    service._repository.invalidate_active.assert_not_called()

    session.commit.assert_not_called()
    session.rollback.assert_called_once()


def test_issue_rolls_back_on_persistence_failure():
    """Reverte a transacao quando a gravacao falha."""

    now = datetime(2026, 10, 9, 12, 0, 0)
    session = Mock()
    code_service = Mock()

    code_service.utc_now.return_value = now
    code_service.generate_verification_id.return_value = "verificacao-001"
    code_service.generate_code.return_value = "012345"
    code_service.expires_at.return_value = now + timedelta(minutes=10)
    code_service.hash_code.return_value = "a" * 64

    service = FotosVerificationIssuanceService(session, code_service)

    service._repository = Mock()
    service._eligibility = Mock()

    service._repository.lock_user.return_value = SimpleNamespace(id="usuario-001")
    service._repository.find_latest.return_value = None
    service._eligibility.can_request.return_value = True
    service._repository.add.side_effect = RuntimeError("Falha simulada na persistencia")

    with pytest.raises(RuntimeError, match="Falha simulada"):
        service.issue(
            user_id="usuario-001",
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    service._repository.invalidate_active.assert_called_once()
    service._repository.add.assert_called_once()

    session.commit.assert_not_called()
    session.rollback.assert_called_once()


def test_issue_rolls_back_on_commit_failure():
    """Reverte a transacao quando o commit falha."""

    now = datetime(2026, 10, 9, 12, 0, 0)
    session = Mock()
    session.commit.side_effect = RuntimeError("Falha simulada no commit")

    code_service = Mock()
    code_service.utc_now.return_value = now
    code_service.generate_verification_id.return_value = "verificacao-001"
    code_service.generate_code.return_value = "012345"
    code_service.expires_at.return_value = now + timedelta(minutes=10)
    code_service.hash_code.return_value = "a" * 64

    service = FotosVerificationIssuanceService(session, code_service)

    service._repository = Mock()
    service._eligibility = Mock()

    service._repository.lock_user.return_value = SimpleNamespace(id="usuario-001")
    service._repository.find_latest.return_value = None
    service._eligibility.can_request.return_value = True

    with pytest.raises(RuntimeError, match="Falha simulada no commit"):
        service.issue(
            user_id="usuario-001",
            purpose=FotosVerificationPurpose.ACTIVATION,
        )

    service._repository.add.assert_called_once()
    session.commit.assert_called_once()
    session.rollback.assert_called_once()


def test_issue_allows_retry_after_failed_delivery():
    """Permite nova emissao quando o envio anterior falhou."""

    now = datetime(2026, 10, 9, 12, 0, 0)
    session = Mock()
    code_service = Mock()
    code_service.utc_now.return_value = now
    code_service.can_resend.return_value = False

    service = FotosVerificationIssuanceService(
        session,
        code_service,
    )

    service._repository = Mock()
    service._eligibility = Mock()

    service._repository.lock_user.return_value = SimpleNamespace(id="usuario-001")
    service._eligibility.can_request.return_value = True
    service._repository.find_latest.return_value = SimpleNamespace(
        created_at=now - timedelta(seconds=30),
        delivery_status="failed",
    )

    service.issue(
        user_id="usuario-001",
        purpose=FotosVerificationPurpose.ACTIVATION,
    )

    code_service.can_resend.assert_not_called()
    service._repository.add.assert_called_once()
    session.commit.assert_called_once()
