from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from jwt.exceptions import MissingRequiredClaimError
from pwdlib import PasswordHash


class PasswordService:
    """Gera e verifica hashes seguros de senhas."""

    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        """Gera o hash seguro de uma senha em texto puro."""

        return self._password_hash.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        """Verifica uma senha em texto puro contra o hash armazenado."""

        return self._password_hash.verify(password, password_hash)


class AccessTokenService:
    """Gera e valida tokens JWT de acesso."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        expire_minutes: int,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    @property
    def expires_in_seconds(self) -> int:
        """Retorna a duração do token em segundos."""

        return self._expire_minutes * 60

    def create(
        self,
        *,
        subject: str,
        organization_id: str | None,
        tenant_id: str | None,
        environment_id: str | None,
        role: str,
    ) -> str:
        """Gera um token de acesso com o escopo institucional do usuário."""

        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(
            minutes=self._expire_minutes
        )

        payload = {
            "sub": subject,
            "organization_id": organization_id,
            "tenant_id": tenant_id,
            "environment_id": environment_id,
            "role": role,
            "type": "access",
            "iat": issued_at,
            "exp": expires_at,
            "jti": str(uuid4()),
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

    def decode(self, token: str) -> dict[str, object]:
        """Decodifica e valida assinatura, expiração e claims obrigatórias."""

        payload = jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
            options={
                "require": [
                    "sub",
                    "role",
                    "type",
                    "iat",
                    "exp",
                    "jti",
                ],
            },
        )

        if "organization_id" not in payload:
            raise MissingRequiredClaimError("organization_id")

        return payload
