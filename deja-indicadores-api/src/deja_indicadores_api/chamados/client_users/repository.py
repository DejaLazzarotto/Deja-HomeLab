from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.chamados.client_users.models import (
    ChamadosClientUserModel,
)


class ChamadosClientUserRepository:
    """Acesso persistente aos vínculos entre usuários e Clientes."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def find_by_user_id(
        self,
        user_id: str,
    ) -> ChamadosClientUserModel | None:
        """Localiza o vínculo existente para um usuário."""

        statement = select(ChamadosClientUserModel).where(
            ChamadosClientUserModel.user_id == user_id
        )

        return self._session.scalar(statement)

    def list_by_client_id(
        self,
        client_id: str,
    ) -> list[ChamadosClientUserModel]:
        """Lista vínculos associados a um Cliente."""

        statement = (
            select(ChamadosClientUserModel)
            .where(
                ChamadosClientUserModel.client_id == client_id
            )
            .order_by(ChamadosClientUserModel.created_at)
        )

        return list(self._session.scalars(statement).all())

    def add(
        self,
        link: ChamadosClientUserModel,
    ) -> ChamadosClientUserModel:
        """Adiciona um vínculo e confirma a transação."""

        self._session.add(link)
        self._session.commit()
        self._session.refresh(link)

        return link

    def update(
        self,
        link: ChamadosClientUserModel,
    ) -> ChamadosClientUserModel:
        """Confirma alterações em um vínculo existente."""

        self._session.commit()
        self._session.refresh(link)

        return link

    def delete(
        self,
        link: ChamadosClientUserModel,
    ) -> None:
        """Remove um vínculo existente."""

        self._session.delete(link)
        self._session.commit()