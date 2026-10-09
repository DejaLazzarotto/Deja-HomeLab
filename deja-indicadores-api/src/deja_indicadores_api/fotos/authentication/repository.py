"""Persistencia dos codigos de verificacao do Fotos PWA."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.authentication.models import (
    FotosVerificationCodeModel,
)
from deja_indicadores_api.user_management.models import UserModel


class FotosVerificationCodeRepository:
    """Gerencia os registros de verificacao no banco."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def lock_user(self, user_id: str) -> UserModel | None:
        """Bloqueia o usuario durante a transacao atual."""

        statement = select(UserModel).where(UserModel.id == user_id).with_for_update()

        return self._session.scalar(statement)

    def add(
        self,
        verification: FotosVerificationCodeModel,
    ) -> FotosVerificationCodeModel:
        """Adiciona uma solicitacao sem confirmar a transacao."""

        self._session.add(verification)
        self._session.flush()

        return verification

    def find_latest(
        self,
        user_id: str,
        purpose: str,
        *,
        for_update: bool = False,
    ) -> FotosVerificationCodeModel | None:
        """Localiza a verificacao mais recente do usuario."""

        statement = (
            select(FotosVerificationCodeModel)
            .where(
                FotosVerificationCodeModel.user_id == user_id,
                FotosVerificationCodeModel.purpose == purpose,
            )
            .order_by(
                FotosVerificationCodeModel.created_at.desc(),
                FotosVerificationCodeModel.id.desc(),
            )
            .limit(1)
        )

        if for_update:
            statement = statement.with_for_update()

        return self._session.scalar(statement)

    def increment_attempts(
        self,
        verification: FotosVerificationCodeModel,
    ) -> None:
        """Registra uma tentativa de verificacao."""

        verification.attempts += 1
        self._session.flush()

    def consume(
        self,
        verification: FotosVerificationCodeModel,
        consumed_at: datetime,
    ) -> None:
        """Marca o codigo como utilizado."""

        verification.consumed_at = consumed_at
        self._session.flush()

    def invalidate_active(
        self,
        user_id: str,
        purpose: str,
        invalidated_at: datetime,
    ) -> None:
        """Invalida codigos anteriores ainda nao utilizados."""

        statement = (
            update(FotosVerificationCodeModel)
            .where(
                FotosVerificationCodeModel.user_id == user_id,
                FotosVerificationCodeModel.purpose == purpose,
                FotosVerificationCodeModel.consumed_at.is_(None),
            )
            .values(consumed_at=invalidated_at)
        )

        self._session.execute(statement)
        self._session.flush()

    def update_delivery_status(
        self,
        verification_id: str,
        status: str,
    ) -> bool:
        """Atualiza somente codigos cuja entrega esta pendente."""

        if status not in ("sent", "failed"):
            raise ValueError("Estado de entrega invalido.")

        statement = (
            update(FotosVerificationCodeModel)
            .where(
                FotosVerificationCodeModel.id == verification_id,
                FotosVerificationCodeModel.delivery_status == "pending",
                FotosVerificationCodeModel.consumed_at.is_(None),
            )
            .values(delivery_status=status)
        )

        result = self._session.execute(statement)
        self._session.flush()

        return result.rowcount == 1
