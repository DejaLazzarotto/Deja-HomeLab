from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.chamados.clients.exceptions import (
    ChamadosClientNotFoundError,
)
from deja_indicadores_api.chamados.clients.models import ChamadosClientModel
from deja_indicadores_api.chamados.clients.repository import (
    ChamadosClientRepository,
)
from deja_indicadores_api.chamados.tickets.service import (
    CHAMADOS_TICKET_ASSIGNEE_ROLES,
    CHAMADOS_TICKET_OPERATOR_ROLES,
)
from deja_indicadores_api.user_management.models import (
    UserModel,
    UserStatus,
)
from deja_indicadores_api.user_management.repository import UserRepository


class ChamadosTicketAssigneeService:
    """Consulta responsáveis que podem receber um chamado."""

    def __init__(
        self,
        client_repository: ChamadosClientRepository,
        user_repository: UserRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._client_repository = client_repository
        self._user_repository = user_repository
        self._authorization_service = authorization_service

    def list(
        self,
        client_id: str,
        current_user: AuthenticatedUser,
    ) -> list[UserModel]:
        """Lista responsáveis elegíveis para o escopo do Cliente."""

        self._authorization_service.require_roles(
            current_user,
            CHAMADOS_TICKET_OPERATOR_ROLES,
        )

        client = self._require_client(client_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=client.organization_id,
            tenant_id=client.tenant_id,
            environment_id=client.environment_id,
        )

        users = self._user_repository.list(
            organization_id=client.organization_id,
            status=UserStatus.ACTIVE,
        )

        return [
            user
            for user in users
            if self._is_eligible(user, client)
        ]

    def _require_client(
        self,
        client_id: str,
    ) -> ChamadosClientModel:
        """Retorna o Cliente usado para definir o escopo."""

        client = self._client_repository.find_by_id(client_id)

        if client is None:
            raise ChamadosClientNotFoundError(client_id)

        return client

    def _is_eligible(
        self,
        user: UserModel,
        client: ChamadosClientModel,
    ) -> bool:
        """Confirma papel e compatibilidade institucional."""

        return (
            user.role in CHAMADOS_TICKET_ASSIGNEE_ROLES
            and user.organization_id == client.organization_id
            and (
                user.tenant_id is None
                or user.tenant_id == client.tenant_id
            )
            and (
                user.environment_id is None
                or user.environment_id == client.environment_id
            )
        )