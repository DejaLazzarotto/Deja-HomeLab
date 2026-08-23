from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from deja_indicadores_api.chamados.clients.models import (
    ChamadosClientModel,
)


class ChamadosClientRepository:
    """Acesso persistente aos clientes do Deja Chamados."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def list(
        self,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        search: str | None = None,
        active: bool | None = None,
    ) -> list[ChamadosClientModel]:
        """Lista clientes dentro dos filtros informados."""

        statement = select(ChamadosClientModel)

        if organization_id is not None:
            statement = statement.where(ChamadosClientModel.organization_id == organization_id)

        if tenant_id is not None:
            statement = statement.where(ChamadosClientModel.tenant_id == tenant_id)

        if environment_id is not None:
            statement = statement.where(ChamadosClientModel.environment_id == environment_id)

        if search is not None:
            search_pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    ChamadosClientModel.company_name.ilike(search_pattern),
                    ChamadosClientModel.fantasy_name.ilike(search_pattern),
                    ChamadosClientModel.document.ilike(search_pattern),
                    ChamadosClientModel.contact_name.ilike(search_pattern),
                    ChamadosClientModel.email.ilike(search_pattern),
                )
            )

        if active is not None:
            statement = statement.where(ChamadosClientModel.active == active)

        statement = statement.order_by(ChamadosClientModel.fantasy_name)

        return list(self._session.scalars(statement).all())

    def find_by_id(
        self,
        client_id: str,
    ) -> ChamadosClientModel | None:
        """Localiza um cliente pelo identificador."""

        return self._session.get(
            ChamadosClientModel,
            client_id,
        )

    def find_by_document(
        self,
        organization_id: str,
        document: str,
    ) -> ChamadosClientModel | None:
        """Localiza um documento dentro da organização."""

        statement = select(ChamadosClientModel).where(
            ChamadosClientModel.organization_id == organization_id,
            ChamadosClientModel.document == document,
        )

        return self._session.scalar(statement)

    def add(
        self,
        client: ChamadosClientModel,
    ) -> ChamadosClientModel:
        """Adiciona e persiste um cliente."""

        self._session.add(client)
        self._session.commit()
        self._session.refresh(client)
        return client

    def update(
        self,
        client: ChamadosClientModel,
    ) -> ChamadosClientModel:
        """Persiste as alterações de um cliente."""

        self._session.commit()
        self._session.refresh(client)
        return client

    def delete(
        self,
        client: ChamadosClientModel,
    ) -> None:
        """Remove um cliente persistentemente."""

        self._session.delete(client)
        self._session.commit()
