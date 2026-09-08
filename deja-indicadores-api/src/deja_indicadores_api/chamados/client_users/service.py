from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.exceptions import (
    AuthorizationError,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.chamados.client_users.exceptions import (
    ChamadosClientUserAlreadyExistsError,
    ChamadosClientUserNotFoundError,
)
from deja_indicadores_api.chamados.client_users.models import (
    ChamadosClientUserModel,
)
from deja_indicadores_api.chamados.client_users.repository import (
    ChamadosClientUserRepository,
)
from deja_indicadores_api.chamados.client_users.schemas import (
    ChamadosClientUserCreate,
    ChamadosClientUserUpdate,
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
from deja_indicadores_api.user_management.exceptions import (
    UserNotFoundError,
)
from deja_indicadores_api.user_management.models import (
    UserModel,
    UserRole,
)
from deja_indicadores_api.user_management.repository import (
    UserRepository,
)


class ChamadosClientUserService:
    """Regras de aplicação para vínculos de usuários externos."""

    def __init__(
        self,
        repository: ChamadosClientUserRepository,
        client_repository: ChamadosClientRepository,
        user_repository: UserRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._client_repository = client_repository
        self._user_repository = user_repository
        self._authorization_service = authorization_service

    def find_by_user_id(
        self,
        user_id: str,
        current_user: AuthenticatedUser,
    ) -> ChamadosClientUserModel:
        """Retorna o vínculo de um usuário dentro do escopo permitido."""

        link = self._require_link(user_id)
        client = self._require_client(link.client_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=client.organization_id,
            tenant_id=client.tenant_id,
            environment_id=client.environment_id,
        )

        return link

    def create(
        self,
        input_data: ChamadosClientUserCreate,
        current_user: AuthenticatedUser,
    ) -> ChamadosClientUserModel:
        """Vincula um usuário client a um Cliente do Chamados."""

        user = self._require_user(input_data.user_id)
        client = self._require_client(input_data.client_id)

        self._require_client_role(user)
        self._require_matching_scope(user, client)

        self._authorization_service.require_scope(
            current_user,
            organization_id=client.organization_id,
            tenant_id=client.tenant_id,
            environment_id=client.environment_id,
        )

        if self._repository.find_by_user_id(user.id) is not None:
            raise ChamadosClientUserAlreadyExistsError(user.id)

        link = ChamadosClientUserModel(
            id=str(uuid4()),
            user_id=user.id,
            client_id=client.id,
        )

        return self._repository.add(link)

    def update(
        self,
        user_id: str,
        input_data: ChamadosClientUserUpdate,
        current_user: AuthenticatedUser,
    ) -> ChamadosClientUserModel:
        """Altera o Cliente vinculado ao usuário externo."""

        link = self._require_link(user_id)
        user = self._require_user(user_id)
        client = self._require_client(input_data.client_id)

        self._require_client_role(user)
        self._require_matching_scope(user, client)

        self._authorization_service.require_scope(
            current_user,
            organization_id=client.organization_id,
            tenant_id=client.tenant_id,
            environment_id=client.environment_id,
        )

        link.client_id = client.id

        return self._repository.update(link)

    def delete(
        self,
        user_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Remove o vínculo de um usuário externo."""

        link = self._require_link(user_id)
        client = self._require_client(link.client_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=client.organization_id,
            tenant_id=client.tenant_id,
            environment_id=client.environment_id,
        )

        self._repository.delete(link)

    def _require_link(
        self,
        user_id: str,
    ) -> ChamadosClientUserModel:
        """Exige um vínculo existente para o usuário."""

        link = self._repository.find_by_user_id(user_id)

        if link is None:
            raise ChamadosClientUserNotFoundError(user_id)

        return link

    def _require_user(
        self,
        user_id: str,
    ) -> UserModel:
        """Exige um usuário existente."""

        user = self._user_repository.find_by_id(user_id)

        if user is None:
            raise UserNotFoundError(user_id)

        return user

    def _require_client(
        self,
        client_id: str,
    ) -> ChamadosClientModel:
        """Exige um Cliente existente."""

        client = self._client_repository.find_by_id(client_id)

        if client is None:
            raise ChamadosClientNotFoundError(client_id)

        return client

    def _require_client_role(
        self,
        user: UserModel,
    ) -> None:
        """Exige que o usuário possua o papel client."""

        if user.role != UserRole.CLIENT:
            raise AuthorizationError

    def _require_matching_scope(
        self,
        user: UserModel,
        client: ChamadosClientModel,
    ) -> None:
        """Exige que usuário e Cliente compartilhem o mesmo escopo."""

        if (
            user.organization_id != client.organization_id
            or user.tenant_id != client.tenant_id
            or user.environment_id != client.environment_id
        ):
            raise AuthorizationError