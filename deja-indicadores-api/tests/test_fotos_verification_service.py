"""Testes do servico de verificacao do Fotos PWA."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from deja_indicadores_api.fotos.authentication.service import (
    FotosVerificationCodeService,
)


def test_generate_six_digit_code():
    """Gera um codigo numerico de seis digitos."""

    with patch(
        "deja_indicadores_api.fotos.authentication.service.secrets.randbelow",
        return_value=12345,
    ) as random_generator:
        code = FotosVerificationCodeService.generate_code()

    assert code == "012345"
    assert len(code) == 6
    assert code.isascii()
    assert code.isdigit()

    random_generator.assert_called_once_with(1_000_000)


def test_hash_and_verify_code():
    """Valida HMAC e impede reutilizacao em outro usuario."""

    service = FotosVerificationCodeService("a" * 64)

    verification_id = "verification-001"
    user_id = "user-001"
    purpose = "activation"
    code = "012345"

    code_hash = service.hash_code(
        verification_id=verification_id,
        user_id=user_id,
        purpose=purpose,
        code=code,
    )

    assert len(code_hash) == 64
    assert code not in code_hash

    assert service.verify_code(
        verification_id=verification_id,
        user_id=user_id,
        purpose=purpose,
        code=code,
        expected_hash=code_hash,
    )

    assert not service.verify_code(
        verification_id=verification_id,
        user_id=user_id,
        purpose=purpose,
        code="999999",
        expected_hash=code_hash,
    )

    assert not service.verify_code(
        verification_id=verification_id,
        user_id="outro-usuario",
        purpose=purpose,
        code=code,
        expected_hash=code_hash,
    )


@pytest.mark.parametrize(
    "invalid_code",
    [
        "",
        "12345",
        "1234567",
        "abcdef",
        "12 456",
        "１２３４５６",
    ],
)
def test_reject_invalid_code_format(invalid_code):
    """Rejeita codigos que nao possuem seis digitos ASCII."""

    service = FotosVerificationCodeService("a" * 64)

    assert not service.verify_code(
        verification_id="verification-001",
        user_id="user-001",
        purpose="activation",
        code=invalid_code,
        expected_hash="0" * 64,
    )


@pytest.mark.parametrize(
    "invalid_key",
    [
        "",
        "senha-curta",
        "g" * 64,
        "a" * 63,
    ],
)
def test_reject_invalid_secret_key(invalid_key):
    """Impede inicializacao com chave HMAC invalida."""

    with pytest.raises(ValueError):
        FotosVerificationCodeService(invalid_key)

def test_code_is_bound_to_purpose_and_verification():
    """Impede reutilizacao do codigo em outra finalidade ou solicitacao."""

    service = FotosVerificationCodeService("a" * 64)

    code_hash = service.hash_code(
        verification_id="solicitacao-1",
        user_id="usuario-1",
        purpose="activation",
        code="012345",
    )

    assert not service.verify_code(
        verification_id="solicitacao-1",
        user_id="usuario-1",
        purpose="password_reset",
        code="012345",
        expected_hash=code_hash,
    )

    assert not service.verify_code(
        verification_id="solicitacao-2",
        user_id="usuario-1",
        purpose="activation",
        code="012345",
        expected_hash=code_hash,
    )

def test_verification_code_expiration():
    """Verifica os limites de validade de dez minutos."""

    service = FotosVerificationCodeService("a" * 64)
    created_at = datetime(2026, 10, 9, 12, 0, 0)
    expires_at = service.expires_at(created_at)

    assert expires_at == created_at + timedelta(minutes=10)

    assert service.is_usable(
        expires_at=expires_at,
        attempts=0,
        consumed_at=None,
        now=created_at + timedelta(minutes=9, seconds=59),
    )

    assert not service.is_usable(
        expires_at=expires_at,
        attempts=0,
        consumed_at=None,
        now=expires_at,
    )


def test_verification_attempts_and_consumption():
    """Bloqueia o codigo apos cinco tentativas ou consumo."""

    service = FotosVerificationCodeService("a" * 64)
    now = datetime(2026, 10, 9, 12, 0, 0)
    expires_at = now + timedelta(minutes=10)

    assert service.is_usable(
        expires_at=expires_at,
        attempts=4,
        consumed_at=None,
        now=now,
    )

    assert not service.is_usable(
        expires_at=expires_at,
        attempts=5,
        consumed_at=None,
        now=now,
    )

    assert not service.is_usable(
        expires_at=expires_at,
        attempts=0,
        consumed_at=now,
        now=now,
    )


def test_verification_resend_interval():
    """Exige intervalo minimo de sessenta segundos."""

    service = FotosVerificationCodeService("a" * 64)
    created_at = datetime(2026, 10, 9, 12, 0, 0)

    assert not service.can_resend(
        created_at=created_at,
        now=created_at + timedelta(seconds=59),
    )

    assert service.can_resend(
        created_at=created_at,
        now=created_at + timedelta(seconds=60),
    )