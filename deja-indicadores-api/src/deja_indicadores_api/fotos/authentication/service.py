"""Geracao e protecao dos codigos de verificacao do Fotos PWA."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4


class FotosVerificationCodeService:
    """Gera, protege e valida regras de codigos temporarios."""

    CODE_TTL = timedelta(minutes=10)
    RESEND_INTERVAL = timedelta(seconds=60)
    MAX_ATTEMPTS = 5

    def __init__(self, secret_key: str) -> None:
        if len(secret_key) != 64 or any(
            character not in "0123456789abcdef" for character in secret_key
        ):
            raise ValueError("A chave de verificacao do Fotos e invalida.")

        self._secret_key = bytes.fromhex(secret_key)

    @staticmethod
    def utc_now() -> datetime:
        """Retorna UTC sem fuso e sem microssegundos."""

        return datetime.now(UTC).replace(
            tzinfo=None,
            microsecond=0,
        )

    @staticmethod
    def generate_code() -> str:
        """Gera um codigo numerico seguro de seis digitos."""

        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def generate_verification_id() -> str:
        """Gera um identificador unico para a solicitacao."""

        return str(uuid4())

    def expires_at(self, created_at: datetime) -> datetime:
        """Calcula a expiracao de uma solicitacao."""

        return created_at + self.CODE_TTL

    def can_resend(
        self,
        *,
        created_at: datetime,
        now: datetime,
    ) -> bool:
        """Verifica o intervalo minimo entre solicitacoes."""

        return now >= created_at + self.RESEND_INTERVAL

    def is_usable(
        self,
        *,
        expires_at: datetime,
        attempts: int,
        consumed_at: datetime | None,
        now: datetime,
    ) -> bool:
        """Verifica se o codigo ainda pode ser utilizado."""

        return consumed_at is None and attempts < self.MAX_ATTEMPTS and now < expires_at

    def hash_code(
        self,
        *,
        verification_id: str,
        user_id: str,
        purpose: str,
        code: str,
    ) -> str:
        """Protege o codigo com HMAC-SHA256."""

        message = (f"{verification_id}:{user_id}:{purpose}:{code}").encode()

        return hmac.new(
            self._secret_key,
            message,
            hashlib.sha256,
        ).hexdigest()

    def verify_code(
        self,
        *,
        verification_id: str,
        user_id: str,
        purpose: str,
        code: str,
        expected_hash: str,
    ) -> bool:
        """Compara o codigo informado com o hash armazenado."""

        if len(code) != 6 or not code.isascii() or not code.isdigit():
            return False

        calculated_hash = self.hash_code(
            verification_id=verification_id,
            user_id=user_id,
            purpose=purpose,
            code=code,
        )

        return hmac.compare_digest(
            calculated_hash,
            expected_hash,
        )
