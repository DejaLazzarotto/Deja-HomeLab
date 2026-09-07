from uuid import uuid7

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.chamados.tickets.exceptions import (
    ChamadosTicketNotFoundError,
)
from deja_indicadores_api.chamados.tickets.models import (
    ChamadosTicketModel,
)
from deja_indicadores_api.chamados.tickets.repository import (
    ChamadosTicketRepository,
)
from deja_indicadores_api.chamados.tickets.timeline.models import (
    ChamadosTicketTimelineModel,
)
from deja_indicadores_api.chamados.tickets.timeline.repository import (
    ChamadosTicketTimelineRepository,
)


class ChamadosTicketTimelineService:
    """Regras de histórico dos chamados do Deja Chamados."""

    def __init__(
        self,
        repository: ChamadosTicketTimelineRepository,
        ticket_repository: ChamadosTicketRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._ticket_repository = ticket_repository
        self._authorization_service = authorization_service

    def list_by_ticket_id(
        self,
        ticket_id: str,
        current_user: AuthenticatedUser,
    ) -> list[ChamadosTicketTimelineModel]:
        """Lista o histórico de um chamado dentro do escopo permitido."""

        ticket = self._require_ticket(ticket_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=ticket.organization_id,
            tenant_id=ticket.tenant_id,
            environment_id=ticket.environment_id,
        )

        return self._repository.list_by_ticket_id(ticket_id)

    def register(
        self,
        *,
        ticket_id: str,
        event_type: str,
        description: str,
        created_by_user_id: str | None = None,
        previous_value: str | None = None,
        new_value: str | None = None,
    ) -> ChamadosTicketTimelineModel:
        """Registra internamente um evento no histórico do chamado."""

        timeline = ChamadosTicketTimelineModel(
            id=str(uuid7()),
            ticket_id=ticket_id,
            event_type=event_type,
            description=description,
            previous_value=previous_value,
            new_value=new_value,
            created_by_user_id=created_by_user_id,
        )

        return self._repository.add(timeline)

    def _require_ticket(
        self,
        ticket_id: str,
    ) -> ChamadosTicketModel:
        """Retorna o chamado pai ou informa sua inexistência."""

        ticket = self._ticket_repository.find_by_id(ticket_id)

        if ticket is None:
            raise ChamadosTicketNotFoundError(ticket_id)

        return ticket
