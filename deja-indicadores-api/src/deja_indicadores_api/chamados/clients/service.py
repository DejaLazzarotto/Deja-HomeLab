from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.chamados.clients.exceptions import (
    ChamadosClientDocumentAlreadyExistsError,
    ChamadosClientNotFoundError,
)
from deja_indicadores_api.chamados.clients.models import (
    ChamadosClientModel,
)
from deja_indicadores_api.chamados.clients.repository import (
    ChamadosClientRepository,
)
from deja_indicadores_api.chamados.clients.schemas import (
    ChamadosClientCreate,
    ChamadosClientUpdate,
)
from deja_indicadores_api.tenant_management.exceptions import (
    EnvironmentNotFoundError,
    TenantNotFoundError,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    TenantModel,
)
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)
from deja_indicadores_api.user_management.models import UserRole

CHAMADOS_CLIENT_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)

CHAMADOS_CLIENT_MANAGER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
    }
)


class ChamadosClientService:
    """Regras de aplicação dos clientes do Deja Chamados."""

    def __init__(
        self,
        repository: ChamadosClientRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._authorization_service = authorization_service

    def list(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        search: str | None = None,
        active: bool | None = None,
    ) -> list[ChamadosClientModel]:
        """Lista clientes dentro do escopo permitido."""

        self._require_roles(
            current_user,
            CHAMADOS_CLIENT_READER_ROLES,
        )
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
            search=search,
            active=active,
        )

    def find_by_id(
        self,
        client_id: str,
        current_user: AuthenticatedUser,
    ) -> ChamadosClientModel:
        """Retorna um cliente dentro do escopo permitido."""

        self._require_roles(
            current_user,
            CHAMADOS_CLIENT_READER_ROLES,
        )
        client = self._find_by_id(client_id)
        environment, tenant = self._resolve_client_scope(client)
        self._require_client_scope(
            current_user,
            environment,
            tenant,
        )

        return client

    def create(
        self,
        input_data: ChamadosClientCreate,
        current_user: AuthenticatedUser,
    ) -> ChamadosClientModel:
        """Cadastra um cliente dentro do escopo permitido."""

        self._require_roles(
            current_user,
            CHAMADOS_CLIENT_MANAGER_ROLES,
        )
        environment = self._require_environment(input_data.environment_id)
        tenant = self._require_tenant(environment.tenant_id)
        self._require_client_scope(
            current_user,
            environment,
            tenant,
        )

        existing_client = self._repository.find_by_document(
            tenant.organization_id,
            input_data.document,
        )

        if existing_client is not None:
            raise ChamadosClientDocumentAlreadyExistsError(input_data.document)

        client = ChamadosClientModel(
            id=str(uuid4()),
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            **input_data.model_dump(),
        )

        return self._repository.add(client)

    def update(
        self,
        client_id: str,
        input_data: ChamadosClientUpdate,
        current_user: AuthenticatedUser,
    ) -> ChamadosClientModel:
        """Atualiza um cliente dentro do escopo permitido."""

        self._require_roles(
            current_user,
            CHAMADOS_CLIENT_MANAGER_ROLES,
        )
        client = self._find_by_id(client_id)

        current_environment, current_tenant = self._resolve_client_scope(client)
        self._require_client_scope(
            current_user,
            current_environment,
            current_tenant,
        )

        target_environment = self._require_environment(input_data.environment_id)
        target_tenant = self._require_tenant(target_environment.tenant_id)
        self._require_client_scope(
            current_user,
            target_environment,
            target_tenant,
        )

        document_owner = self._repository.find_by_document(
            target_tenant.organization_id,
            input_data.document,
        )

        if document_owner is not None and document_owner.id != client_id:
            raise ChamadosClientDocumentAlreadyExistsError(input_data.document)

        for (
            field_name,
            value,
        ) in input_data.model_dump().items():
            setattr(
                client,
                field_name,
                value,
            )

        client.organization_id = target_tenant.organization_id
        client.tenant_id = target_tenant.id

        return self._repository.update(client)

    def delete(
        self,
        client_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exclui um cliente dentro do escopo permitido."""

        self._require_roles(
            current_user,
            CHAMADOS_CLIENT_MANAGER_ROLES,
        )
        client = self._find_by_id(client_id)
        environment, tenant = self._resolve_client_scope(client)
        self._require_client_scope(
            current_user,
            environment,
            tenant,
        )

        self._repository.delete(client)

    def _find_by_id(
        self,
        client_id: str,
    ) -> ChamadosClientModel:
        """Retorna um cliente existente sem aplicar autorização."""

        client = self._repository.find_by_id(client_id)

        if client is None:
            raise ChamadosClientNotFoundError(client_id)

        return client

    def _require_environment(
        self,
        environment_id: str,
    ) -> EnvironmentModel:
        """Garante que o ambiente informado exista."""

        environment = self._environment_repository.find_by_id(environment_id)

        if environment is None:
            raise EnvironmentNotFoundError(environment_id)

        return environment

    def _require_tenant(
        self,
        tenant_id: str,
    ) -> TenantModel:
        """Garante que o tenant informado exista."""

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        return tenant

    def _resolve_client_scope(
        self,
        client: ChamadosClientModel,
    ) -> tuple[EnvironmentModel, TenantModel]:
        """Resolve a hierarquia institucional real do cliente."""

        environment = self._require_environment(client.environment_id)
        tenant = self._require_tenant(environment.tenant_id)

        return environment, tenant

    def _require_roles(
        self,
        current_user: AuthenticatedUser,
        allowed_roles: frozenset[UserRole],
    ) -> None:
        """Exige um papel permitido para a operação."""

        self._authorization_service.require_roles(
            current_user,
            allowed_roles,
        )

    def _require_client_scope(
        self,
        current_user: AuthenticatedUser,
        environment: EnvironmentModel,
        tenant: TenantModel,
    ) -> None:
        """Exige acesso à hierarquia institucional do cliente."""

        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )
