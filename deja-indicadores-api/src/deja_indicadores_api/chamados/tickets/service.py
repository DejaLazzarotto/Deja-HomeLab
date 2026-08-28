from datetime import UTC, datetime
from uuid import uuid4

from deja_indicadores_api.authentication.authorization import AuthorizationService
from deja_indicadores_api.authentication.exceptions import AuthorizationError
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.chamados.clients.exceptions import ChamadosClientNotFoundError
from deja_indicadores_api.chamados.clients.models import ChamadosClientModel
from deja_indicadores_api.chamados.clients.repository import ChamadosClientRepository
from deja_indicadores_api.chamados.tickets.enums import (
    ChamadosTicketPriority,
    ChamadosTicketStatus,
)
from deja_indicadores_api.chamados.tickets.exceptions import (
    ChamadosTicketAssignedUserNotFoundError,
    ChamadosTicketInactiveClientError,
    ChamadosTicketInvalidAssignedUserError,
    ChamadosTicketInvalidStatusTransitionError,
    ChamadosTicketNotFoundError,
)
from deja_indicadores_api.chamados.tickets.models import ChamadosTicketModel
from deja_indicadores_api.chamados.tickets.repository import ChamadosTicketRepository
from deja_indicadores_api.chamados.tickets.schemas import (
    ChamadosTicketCreate,
    ChamadosTicketStatusUpdate,
    ChamadosTicketUpdate,
)
from deja_indicadores_api.user_management.models import (
    UserModel,
    UserRole,
    UserStatus,
)
from deja_indicadores_api.user_management.repository import UserRepository

CHAMADOS_TICKET_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)

CHAMADOS_TICKET_OPERATOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
    }
)

CHAMADOS_TICKET_ASSIGNEE_ROLES = frozenset(
    {
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
    }
)

ALLOWED_STATUS_TRANSITIONS = {
    ChamadosTicketStatus.OPEN: frozenset(
        {
            ChamadosTicketStatus.IN_PROGRESS,
            ChamadosTicketStatus.PENDING,
            ChamadosTicketStatus.CLOSED,
        }
    ),
    ChamadosTicketStatus.IN_PROGRESS: frozenset(
        {
            ChamadosTicketStatus.OPEN,
            ChamadosTicketStatus.PENDING,
            ChamadosTicketStatus.CLOSED,
        }
    ),
    ChamadosTicketStatus.PENDING: frozenset(
        {
            ChamadosTicketStatus.OPEN,
            ChamadosTicketStatus.IN_PROGRESS,
            ChamadosTicketStatus.CLOSED,
        }
    ),
    ChamadosTicketStatus.CLOSED: frozenset(
        {
            ChamadosTicketStatus.OPEN,
        }
    ),
}


class ChamadosTicketService:
    """Regras de aplicação dos chamados do Deja Chamados."""

    def __init__(
        self,
        repository: ChamadosTicketRepository,
        client_repository: ChamadosClientRepository,
        user_repository: UserRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._client_repository = client_repository
        self._user_repository = user_repository
        self._authorization_service = authorization_service

    def list(
        self,
        current_user: AuthenticatedUser,
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
        """Lista chamados dentro do escopo permitido."""

        self._require_roles(current_user, CHAMADOS_TICKET_READER_ROLES)
        (
            effective_organization_id,
            effective_tenant_id,
            effective_environment_id,
        ) = self._authorization_service.resolve_list_scope(
            current_user,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )

        return self._repository.list(
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
            client_id=client_id,
            status=status,
            priority=priority,
            assigned_to_user_id=assigned_to_user_id,
            search=search,
        )

    def find_by_id(
        self,
        ticket_id: str,
        current_user: AuthenticatedUser,
    ) -> ChamadosTicketModel:
        """Retorna um chamado dentro do escopo permitido."""

        self._require_roles(current_user, CHAMADOS_TICKET_READER_ROLES)
        ticket = self._find_by_id(ticket_id)
        self._require_ticket_scope(current_user, ticket)
        return ticket

    def create(
        self,
        input_data: ChamadosTicketCreate,
        current_user: AuthenticatedUser,
    ) -> ChamadosTicketModel:
        """Abre um chamado dentro do escopo permitido."""

        self._require_roles(current_user, CHAMADOS_TICKET_OPERATOR_ROLES)
        client = self._require_client(input_data.client_id)

        if input_data.environment_id != client.environment_id:
            raise AuthorizationError

        self._authorization_service.require_scope(
            current_user,
            organization_id=client.organization_id,
            tenant_id=client.tenant_id,
            environment_id=client.environment_id,
        )

        if not client.active:
            raise ChamadosTicketInactiveClientError(client.id)

        assigned_user = self._resolve_assigned_user(
            input_data.assigned_to_user_id,
            client,
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
            priority=input_data.priority,
            opened_by_user_id=current_user.id,
            assigned_to_user_id=(
                assigned_user.id if assigned_user is not None else None
            ),
            closed_by_user_id=None,
            closed_at=None,
        )

        return self._repository.add(ticket)

    def update(
        self,
        ticket_id: str,
        input_data: ChamadosTicketUpdate,
        current_user: AuthenticatedUser,
    ) -> ChamadosTicketModel:
        """Atualiza os dados operacionais de um chamado."""

        self._require_roles(current_user, CHAMADOS_TICKET_OPERATOR_ROLES)
        ticket = self._find_by_id(ticket_id)
        self._require_ticket_scope(current_user, ticket)
        client = self._require_client(ticket.client_id)
        self._require_ticket_client_scope(ticket, client)
        assigned_user = self._resolve_assigned_user(
            input_data.assigned_to_user_id,
            client,
        )

        ticket.title = input_data.title
        ticket.description = input_data.description
        ticket.priority = input_data.priority
        ticket.assigned_to_user_id = (
            assigned_user.id if assigned_user is not None else None
        )

        return self._repository.update(ticket)

    def update_status(
        self,
        ticket_id: str,
        input_data: ChamadosTicketStatusUpdate,
        current_user: AuthenticatedUser,
    ) -> ChamadosTicketModel:
        """Altera o estado de um chamado autorizado."""

        self._require_roles(current_user, CHAMADOS_TICKET_OPERATOR_ROLES)
        ticket = self._find_by_id(ticket_id)
        self._require_ticket_scope(current_user, ticket)

        current_status = ticket.status
        target_status = input_data.status

        if target_status == current_status:
            return ticket

        if target_status not in ALLOWED_STATUS_TRANSITIONS[current_status]:
            raise ChamadosTicketInvalidStatusTransitionError(
                current_status.value,
                target_status.value,
            )

        ticket.status = target_status

        if target_status == ChamadosTicketStatus.CLOSED:
            ticket.closed_by_user_id = current_user.id
            ticket.closed_at = datetime.now(UTC).replace(tzinfo=None)
        else:
            ticket.closed_by_user_id = None
            ticket.closed_at = None

        return self._repository.update(ticket)

    def _find_by_id(self, ticket_id: str) -> ChamadosTicketModel:
        """Retorna um chamado existente sem aplicar autorização."""

        ticket = self._repository.find_by_id(ticket_id)

        if ticket is None:
            raise ChamadosTicketNotFoundError(ticket_id)

        return ticket

    def _require_client(self, client_id: str) -> ChamadosClientModel:
        """Retorna o Cliente vinculado ao chamado."""

        client = self._client_repository.find_by_id(client_id)

        if client is None:
            raise ChamadosClientNotFoundError(client_id)

        return client

    def _resolve_assigned_user(
        self,
        user_id: str | None,
        client: ChamadosClientModel,
    ) -> UserModel | None:
        """Valida e retorna o responsável informado."""

        if user_id is None:
            return None

        user = self._user_repository.find_by_id(user_id)

        if user is None:
            raise ChamadosTicketAssignedUserNotFoundError(user_id)

        if (
            user.status != UserStatus.ACTIVE
            or user.role not in CHAMADOS_TICKET_ASSIGNEE_ROLES
            or user.organization_id != client.organization_id
            or (user.tenant_id is not None and user.tenant_id != client.tenant_id)
            or (
                user.environment_id is not None
                and user.environment_id != client.environment_id
            )
        ):
            raise ChamadosTicketInvalidAssignedUserError(user_id)

        return user

    def _require_ticket_scope(
        self,
        current_user: AuthenticatedUser,
        ticket: ChamadosTicketModel,
    ) -> None:
        """Exige acesso ao escopo institucional do chamado."""

        self._authorization_service.require_scope(
            current_user,
            organization_id=ticket.organization_id,
            tenant_id=ticket.tenant_id,
            environment_id=ticket.environment_id,
        )

    def _require_ticket_client_scope(
        self,
        ticket: ChamadosTicketModel,
        client: ChamadosClientModel,
    ) -> None:
        """Garante que chamado e Cliente compartilhem o mesmo escopo."""

        if (
            ticket.organization_id != client.organization_id
            or ticket.tenant_id != client.tenant_id
            or ticket.environment_id != client.environment_id
        ):
            raise AuthorizationError

    def _require_roles(
        self,
        current_user: AuthenticatedUser,
        allowed_roles: frozenset[UserRole],
    ) -> None:
        """Exige um papel permitido para a operação."""

        self._authorization_service.require_roles(current_user, allowed_roles)