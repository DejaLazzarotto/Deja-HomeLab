from uuid import uuid4

from deja_indicadores_api.authentication.exceptions import (
    AuthorizationError,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.chamados.client_users.exceptions import (
    ChamadosClientUserNotFoundError,
)
from deja_indicadores_api.chamados.client_users.repository import (
    ChamadosClientUserRepository,
)
from deja_indicadores_api.chamados.clients.exceptions import (
    ChamadosClientNotFoundError,
)
from deja_indicadores_api.chamados.clients.models import (
    ChamadosClientModel,
)
from deja_indicadores_api.chamados.clients.repository import (
    ChamadosClientRepository,
)
from deja_indicadores_api.chamados.portal.schemas import (
    ChamadosPortalTicketCreate,
    ChamadosPortalTimelineResponse,
)
from deja_indicadores_api.chamados.tickets.enums import (
    ChamadosTicketPriority,
    ChamadosTicketStatus,
)
from deja_indicadores_api.chamados.tickets.exceptions import (
    ChamadosTicketInactiveClientError,
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
from deja_indicadores_api.chamados.tickets.timeline.service import (
    ChamadosTicketTimelineService,
)
from deja_indicadores_api.user_management.models import (
    UserRole,
)
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)


class ChamadosPortalService:
    """Regras de aplicação do Portal externo do Deja Chamados."""

    def __init__(
        self,
        ticket_repository: ChamadosTicketRepository,
        client_repository: ChamadosClientRepository,
        client_user_repository: ChamadosClientUserRepository,
        timeline_service: ChamadosTicketTimelineService,
        user_repository: UserRepository,
    ) -> None:
        self._ticket_repository = ticket_repository
        self._client_repository = client_repository
        self._client_user_repository = client_user_repository
        self._timeline_service = timeline_service
        self._user_repository = user_repository

    def list_tickets(
        self,
        current_user: AuthenticatedUser,
    ) -> list[ChamadosTicketModel]:
        """Lista somente os chamados do Cliente vinculado ao usuário."""

        client = self._require_portal_client(current_user)

        return self._ticket_repository.list(
            organization_id=client.organization_id,
            tenant_id=client.tenant_id,
            environment_id=client.environment_id,
            client_id=client.id,
        )

    def find_ticket_by_id(
        self,
        ticket_id: str,
        current_user: AuthenticatedUser,
    ) -> ChamadosTicketModel:
        """Retorna um chamado somente quando pertence ao Cliente vinculado."""

        client = self._require_portal_client(current_user)

        ticket = self._ticket_repository.find_by_id(
            ticket_id,
        )

        if ticket is None:
            raise ChamadosTicketNotFoundError(ticket_id)

        if (
            ticket.organization_id != client.organization_id
            or ticket.tenant_id != client.tenant_id
            or ticket.environment_id != client.environment_id
            or ticket.client_id != client.id
        ):
            raise AuthorizationError

        return ticket

    def list_ticket_timeline(
        self,
        ticket_id: str,
        current_user: AuthenticatedUser,
    ) -> list[ChamadosPortalTimelineResponse]:
        """Lista o histórico seguro de um chamado pertencente ao Cliente."""

        self.find_ticket_by_id(
            ticket_id,
            current_user,
        )

        timeline = self._timeline_service.list_by_ticket_id(
            ticket_id,
            current_user,
        )

        return [
            self._map_timeline_event(event)
            for event in timeline
        ]

    def create_ticket(
        self,
        input_data: ChamadosPortalTicketCreate,
        current_user: AuthenticatedUser,
    ) -> ChamadosTicketModel:
        """Abre um chamado para o Cliente vinculado ao usuário."""

        client = self._require_portal_client(current_user)

        if not client.active:
            raise ChamadosTicketInactiveClientError(
                client.id,
            )

        ticket = ChamadosTicketModel(
            id=str(uuid4()),
            organization_id=client.organization_id,
            tenant_id=client.tenant_id,
            environment_id=client.environment_id,
            client_id=client.id,
            title=input_data.title,
            description=input_data.description,
            status=ChamadosTicketStatus.OPEN,
            priority=ChamadosTicketPriority.MEDIUM,
            opened_by_user_id=current_user.id,
            assigned_to_user_id=None,
            closed_by_user_id=None,
            closed_at=None,
        )

        self._ticket_repository.add(ticket)

        self._timeline_service.register(
            ticket_id=ticket.id,
            event_type="created",
            description="Chamado criado pelo Portal.",
            created_by_user_id=current_user.id,
            new_value="created",
        )

        return self._ticket_repository.commit(
            ticket,
        )

    def _map_timeline_event(
        self,
        event: ChamadosTicketTimelineModel,
    ) -> ChamadosPortalTimelineResponse:
        """Converte um evento interno para a representação segura do Portal."""

        previous_value = event.previous_value
        new_value = event.new_value

        if event.event_type == "assigned_changed":
            previous_value = self._resolve_user_name(
                event.previous_value,
            )
            new_value = self._resolve_user_name(
                event.new_value,
            )

        return ChamadosPortalTimelineResponse(
            id=event.id,
            event_type=event.event_type,
            description=event.description,
            previous_value=previous_value,
            new_value=new_value,
            created_at=event.created_at,
        )

    def _resolve_user_name(
        self,
        user_id: str | None,
    ) -> str | None:
        """Converte um identificador interno de usuário em nome público."""

        if user_id is None:
            return None

        user = self._user_repository.find_by_id(
            user_id,
        )

        if user is None:
            return None

        return user.name

    def _require_portal_client(
        self,
        current_user: AuthenticatedUser,
    ) -> ChamadosClientModel:
        """Resolve e valida o Cliente associado ao usuário externo."""

        if current_user.role != UserRole.CLIENT:
            raise AuthorizationError

        link = self._client_user_repository.find_by_user_id(
            current_user.id,
        )

        if link is None:
            raise ChamadosClientUserNotFoundError(
                current_user.id,
            )

        client = self._client_repository.find_by_id(
            link.client_id,
        )

        if client is None:
            raise ChamadosClientNotFoundError(
                link.client_id,
            )

        if (
            current_user.organization_id != client.organization_id
            or current_user.tenant_id != client.tenant_id
            or current_user.environment_id != client.environment_id
        ):
            raise AuthorizationError

        return client