"""Limites de solicitacoes da autenticacao do Fotos PWA."""

import hashlib
import hmac
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session, sessionmaker

from deja_indicadores_api.fotos.authentication.rate_limit_repository import (
    FotosAuthRateLimitRepository,
)


class FotosAuthRateLimitService:
    """Aplica limites persistentes por IP e por conta."""

    IP_LIMIT = 10
    IP_WINDOW_MINUTES = 10

    ACCOUNT_LIMIT = 3
    ACCOUNT_WINDOW_MINUTES = 15

    CONFIRM_IP_LIMIT = 30
    CONFIRM_IP_WINDOW_MINUTES = 10

    CONFIRM_ACCOUNT_LIMIT = 10
    CONFIRM_ACCOUNT_WINDOW_MINUTES = 15

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        secret_key: str,
    ) -> None:
        if not secret_key:
            raise ValueError("Chave de protecao dos identificadores ausente.")

        self._session_factory = session_factory
        self._secret_key = secret_key.encode("utf-8")

    def allow_request(
        self,
        *,
        client_ip: str,
        organization_code: str,
        email: str,
        now: datetime | None = None,
    ) -> bool:
        """Registra a tentativa e verifica os limites aplicaveis."""

        current = now or datetime.now(UTC)

        normalized_ip = client_ip.strip()
        normalized_organization = organization_code.strip().casefold()
        normalized_email = email.strip().casefold()

        if not normalized_ip or not normalized_organization or not normalized_email:
            raise ValueError("Identificadores de requisicao invalidos.")

        ip_hash = self._hash_subject(
            scope="ip",
            subject=normalized_ip,
        )

        account_hash = self._hash_subject(
            scope="account",
            subject=f"{normalized_organization}:{normalized_email}",
        )

        ip_allowed = self._consume(
            scope="ip",
            subject_hash=ip_hash,
            window_start=self._window_start(
                current,
                self.IP_WINDOW_MINUTES,
            ),
            limit=self.IP_LIMIT,
        )

        account_allowed = self._consume(
            scope="account",
            subject_hash=account_hash,
            window_start=self._window_start(
                current,
                self.ACCOUNT_WINDOW_MINUTES,
            ),
            limit=self.ACCOUNT_LIMIT,
        )

        return ip_allowed and account_allowed

    def allow_confirmation(
        self,
        *,
        client_ip: str,
        organization_code: str,
        email: str,
        now: datetime | None = None,
    ) -> bool:
        """Registra e limita tentativas de confirmacao de codigos."""

        current = now or datetime.now(UTC)

        normalized_ip = client_ip.strip()
        normalized_organization = organization_code.strip().casefold()
        normalized_email = email.strip().casefold()

        if not normalized_ip or not normalized_organization or not normalized_email:
            raise ValueError("Identificadores de requisicao invalidos.")

        ip_hash = self._hash_subject(
            scope="confirm_ip",
            subject=normalized_ip,
        )

        account_hash = self._hash_subject(
            scope="confirm_account",
            subject=f"{normalized_organization}:{normalized_email}",
        )

        ip_allowed = self._consume(
            scope="confirm_ip",
            subject_hash=ip_hash,
            window_start=self._window_start(
                current,
                self.CONFIRM_IP_WINDOW_MINUTES,
            ),
            limit=self.CONFIRM_IP_LIMIT,
        )

        account_allowed = self._consume(
            scope="confirm_account",
            subject_hash=account_hash,
            window_start=self._window_start(
                current,
                self.CONFIRM_ACCOUNT_WINDOW_MINUTES,
            ),
            limit=self.CONFIRM_ACCOUNT_LIMIT,
        )

        return ip_allowed and account_allowed

    def _hash_subject(self, *, scope: str, subject: str) -> str:
        payload = f"fotos-auth-rate-limit:{scope}:{subject}"

        return hmac.new(
            self._secret_key,
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _consume(
        self,
        *,
        scope: str,
        subject_hash: str,
        window_start: datetime,
        limit: int,
    ) -> bool:
        with self._session_factory() as session:
            repository = FotosAuthRateLimitRepository(session)

            return repository.consume(
                scope=scope,
                subject_hash=subject_hash,
                window_start=window_start,
                limit=limit,
            )

    @staticmethod
    def _window_start(current: datetime, minutes: int) -> datetime:
        """Calcula o inicio da janela fixa em UTC."""

        if current.tzinfo is None:
            raise ValueError("A data deve conter informacao de fuso horario.")

        utc_current = current.astimezone(UTC)
        midnight = utc_current.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        elapsed = utc_current - midnight
        window_seconds = minutes * 60
        elapsed_seconds = int(elapsed.total_seconds())

        return (
            midnight + timedelta(seconds=(elapsed_seconds // window_seconds) * window_seconds)
        ).replace(tzinfo=None)
