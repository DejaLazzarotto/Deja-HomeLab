"""Contadores atomicos de requisicoes da autenticacao Fotos."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.authentication.rate_limit_models import (
    FotosAuthRateLimitModel,
)


class FotosAuthRateLimitRepository:
    """Controla limites compartilhados de requisicoes no MySQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def consume(
        self,
        *,
        scope: str,
        subject_hash: str,
        window_start: datetime,
        limit: int,
    ) -> bool:
        """Consome uma permissao dentro da janela informada."""

        if scope not in ("ip", "account", "confirm_ip", "confirm_account"):
            raise ValueError("Escopo de limitacao invalido.")

        if limit < 1:
            raise ValueError("Limite de requisicoes invalido.")

        table = FotosAuthRateLimitModel.__table__

        try:
            statement = insert(table).values(
                id=str(uuid4()),
                scope=scope,
                subject_hash=subject_hash,
                window_start=window_start,
                request_count=1,
            )

            statement = statement.on_duplicate_key_update(
                request_count=func.least(
                    table.c.request_count + 1,
                    limit + 1,
                ),
            )

            self._session.execute(statement)

            count = self._session.scalar(
                select(table.c.request_count).where(
                    table.c.scope == scope,
                    table.c.subject_hash == subject_hash,
                    table.c.window_start == window_start,
                )
            )

            allowed = count is not None and count <= limit

            self._session.commit()

            return allowed

        except Exception:
            self._session.rollback()
            raise
