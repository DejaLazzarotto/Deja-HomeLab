from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.chamados.tickets.comments.models import (
    ChamadosTicketCommentModel,
)
from deja_indicadores_api.chamados.tickets.comments.repository import (
    ChamadosTicketCommentRepository,
)
from deja_indicadores_api.chamados.tickets.comments.schemas import (
    ChamadosTicketCommentCreate,
    ChamadosTicketCommentResponse,
)
from deja_indicadores_api.chamados.tickets.exceptions import (
    ChamadosTicketNotFoundError,
)
from deja_indicadores_api.chamados.tickets.repository import (
    ChamadosTicketRepository,
)
from deja_indicadores_api.chamados.tickets.service import (
    CHAMADOS_TICKET_OPERATOR_ROLES,
    CHAMADOS_TICKET_READER_ROLES,
)
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)


class ChamadosTicketCommentService:
    """Regras de aplicação dos comentários de chamados."""

    def __init__(
        self,
        repository: ChamadosTicketCommentRepository,
        ticket_repository: ChamadosTicketRepository,
        authorization_service: AuthorizationService,
        user_repository: UserRepository,
    ) -> None:
        self._repository = repository
        self._ticket_repository = ticket_repository
        self._authorization_service = authorization_service
        self._user_repository = user_repository

    def list_by_ticket_id(
        self,
        ticket_id: str,
        current_user: AuthenticatedUser,
    ) -> list[ChamadosTicketCommentResponse]:
        """Lista comentários de um chamado autorizado."""

        self._authorization_service.require_roles(
            current_user,
            CHAMADOS_TICKET_READER_ROLES,
        )

        ticket = self._require_ticket(ticket_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=ticket.organization_id,
            tenant_id=ticket.tenant_id,
            environment_id=ticket.environment_id,
        )

        comments = self._repository.list_by_ticket_id(
            ticket_id,
        )

        return [
            self._map_comment(comment)
            for comment in comments
        ]

    def create(
        self,
        ticket_id: str,
        input_data: ChamadosTicketCommentCreate,
        current_user: AuthenticatedUser,
    ) -> ChamadosTicketCommentResponse:
        """Adiciona um comentário a um chamado autorizado."""

        self._authorization_service.require_roles(
            current_user,
            CHAMADOS_TICKET_OPERATOR_ROLES,
        )

        ticket = self._require_ticket(ticket_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=ticket.organization_id,
            tenant_id=ticket.tenant_id,
            environment_id=ticket.environment_id,
        )

        comment = ChamadosTicketCommentModel(
            id=str(uuid4()),
            ticket_id=ticket.id,
            content=input_data.content,
            visibility=input_data.visibility,
            created_by_user_id=current_user.id,
        )

        self._repository.add(comment)

        comment = self._repository.commit(
            comment,
        )

        return self._map_comment(comment)

    def _map_comment(
        self,
        comment: ChamadosTicketCommentModel,
    ) -> ChamadosTicketCommentResponse:
        """Converte comentário persistido para resposta administrativa."""

        return ChamadosTicketCommentResponse(
            id=comment.id,
            ticket_id=comment.ticket_id,
            content=comment.content,
            visibility=comment.visibility,
            created_by_user_id=comment.created_by_user_id,
            created_by=self._resolve_user_name(
                comment.created_by_user_id,
            ),
            created_at=comment.created_at,
        )

    def _resolve_user_name(
        self,
        user_id: str | None,
    ) -> str | None:
        """Resolve o nome do autor do comentário."""

        if user_id is None:
            return None

        user = self._user_repository.find_by_id(
            user_id,
        )

        if user is None:
            return None

        return user.name

    def _require_ticket(
        self,
        ticket_id: str,
    ):
        """Retorna um chamado existente."""

        ticket = self._ticket_repository.find_by_id(
            ticket_id,
        )

        if ticket is None:
            raise ChamadosTicketNotFoundError(
                ticket_id,
            )

        return ticket