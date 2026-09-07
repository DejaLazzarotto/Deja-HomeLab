from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from deja_indicadores_api.chamados.tickets.enums import (
    ChamadosTicketPriority,
    ChamadosTicketStatus,
)
from deja_indicadores_api.chamados.tickets.models import (
    ChamadosTicketModel,
)


class ChamadosTicketRepository:
    """Acesso persistente aos chamados do Deja Chamados."""

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
        client_id: str | None = None,
        status: ChamadosTicketStatus | None = None,
        priority: ChamadosTicketPriority | None = None,
        assigned_to_user_id: str | None = None,
        search: str | None = None,
    ) -> list[ChamadosTicketModel]:
        """Lista chamados dentro dos filtros informados."""

        statement = select(ChamadosTicketModel)

        if organization_id is not None:
            statement = statement.where(
                ChamadosTicketModel.organization_id == organization_id
            )

        if tenant_id is not None:
            statement = statement.where(
                ChamadosTicketModel.tenant_id == tenant_id
            )

        if environment_id is not None:
            statement = statement.where(
                ChamadosTicketModel.environment_id == environment_id
            )

        if client_id is not None:
            statement = statement.where(
                ChamadosTicketModel.client_id == client_id
            )

        if status is not None:
            statement = statement.where(
                ChamadosTicketModel.status == status
            )

        if priority is not None:
            statement = statement.where(
                ChamadosTicketModel.priority == priority
            )

        if assigned_to_user_id is not None:
            statement = statement.where(
                ChamadosTicketModel.assigned_to_user_id
                == assigned_to_user_id
            )

        if search is not None:
            search_pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    ChamadosTicketModel.title.ilike(search_pattern),
                    ChamadosTicketModel.description.ilike(search_pattern),
                )
            )

        statement = statement.order_by(
            ChamadosTicketModel.created_at.desc(),
            ChamadosTicketModel.id.desc(),
        )

        return list(self._session.scalars(statement).all())

    def find_by_id(
        self,
        ticket_id: str,
    ) -> ChamadosTicketModel | None:
        """Localiza um chamado pelo identificador."""

        return self._session.get(
            ChamadosTicketModel,
            ticket_id,
        )

    def add(
        self,
        ticket: ChamadosTicketModel,
    ) -> ChamadosTicketModel:
        """Adiciona um chamado sem finalizar a transação."""

        self._session.add(ticket)
        self._session.flush()
        self._session.refresh(ticket)
        return ticket

    def update(
        self,
        ticket: ChamadosTicketModel,
    ) -> ChamadosTicketModel:
        """Sincroniza alterações sem finalizar a transação."""

        self._session.flush()
        return ticket

    def commit(
        self,
        ticket: ChamadosTicketModel,
    ) -> ChamadosTicketModel:
        """Confirma a transação e atualiza o estado persistido."""

        self._session.commit()
        self._session.refresh(ticket)
        return ticket
