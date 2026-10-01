"""Regras de cadastro e associação de Pessoas do Deja Fotos."""

from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.core.exceptions import ResourceConflictError
from deja_indicadores_api.fotos.media.exceptions import (
    FotosMediaNotFoundError,
)
from deja_indicadores_api.fotos.media.repository import (
    FotosMediaRepository,
)
from deja_indicadores_api.fotos.people.exceptions import (
    FotosPersonAlreadyExistsError,
    FotosPersonMediaAlreadyLinkedError,
    FotosPersonMediaLinkNotFoundError,
    FotosPersonMediaScopeMismatchError,
    FotosPersonNotFoundError,
)
from deja_indicadores_api.fotos.people.models import (
    FotosPersonMediaModel,
    FotosPersonModel,
)
from deja_indicadores_api.fotos.people.repository import (
    FotosPersonRepository,
)
from deja_indicadores_api.fotos.people.schemas import (
    FotosPersonCreate,
    FotosPersonUpdate,
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
from deja_indicadores_api.user_management.models import UserModuleRole

FOTOS_MODULE_KEY = "fotos"

PERSON_READER_ROLES = frozenset(
    {
        UserModuleRole.MANAGER,
        UserModuleRole.ANALYST,
        UserModuleRole.VIEWER,
    }
)

PERSON_EDITOR_ROLES = frozenset(
    {
        UserModuleRole.MANAGER,
        UserModuleRole.ANALYST,
    }
)

PERSON_MANAGER_ROLES = frozenset(
    {
        UserModuleRole.MANAGER,
    }
)


class FotosPersonService:
    """Aplica permissões e isolamento institucional a Pessoas."""

    def __init__(
        self,
        repository: FotosPersonRepository,
        media_repository: FotosMediaRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._media_repository = media_repository
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
        active: bool | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[FotosPersonModel], int]:
        self._require_roles(current_user, PERSON_READER_ROLES)

        organization_id, tenant_id, environment_id = (
            self._authorization_service.resolve_list_scope(
                current_user,
                organization_id=organization_id,
                tenant_id=tenant_id,
                environment_id=environment_id,
            )
        )

        return self._repository.list(
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
            active=active,
            name=name,
            page=page,
            page_size=page_size,
        )

    def find_by_id(
        self,
        person_id: str,
        current_user: AuthenticatedUser,
    ) -> FotosPersonModel:
        self._require_roles(current_user, PERSON_READER_ROLES)
        person = self._repository.find_by_id(person_id)

        if person is None:
            raise FotosPersonNotFoundError(person_id)

        environment, tenant = self._resolve_scope(person.environment_id)

        if (
            person.organization_id != tenant.organization_id
            or person.tenant_id != tenant.id
        ):
            raise FotosPersonNotFoundError(person_id)

        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )

        return person

    def create(
        self,
        payload: FotosPersonCreate,
        current_user: AuthenticatedUser,
    ) -> FotosPersonModel:
        self._require_roles(current_user, PERSON_EDITOR_ROLES)
        environment, tenant = self._resolve_scope(payload.environment_id)
        self._require_scope(current_user, environment, tenant)

        existing = self._repository.find_by_scope_and_name(
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
            name=payload.name,
        )
        if existing is not None:
            raise FotosPersonAlreadyExistsError(payload.name)

        person = FotosPersonModel(
            id=str(uuid4()),
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
            name=payload.name,
            description=payload.description,
            active=payload.active,
        )
        return self._repository.add(person)

    def update(
        self,
        person_id: str,
        payload: FotosPersonUpdate,
        current_user: AuthenticatedUser,
    ) -> FotosPersonModel:
        self._require_roles(current_user, PERSON_EDITOR_ROLES)
        person = self.find_by_id(person_id, current_user)

        if payload.environment_id != person.environment_id:
            raise ResourceConflictError(
                "O ambiente de uma pessoa cadastrada não pode ser alterado."
            )

        existing = self._repository.find_by_scope_and_name(
            organization_id=person.organization_id,
            tenant_id=person.tenant_id,
            environment_id=person.environment_id,
            name=payload.name,
        )
        if existing is not None and existing.id != person.id:
            raise FotosPersonAlreadyExistsError(payload.name)

        person.name = payload.name
        person.description = payload.description
        person.active = payload.active
        return self._repository.update(person)

    def delete(
        self,
        person_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        self._require_roles(current_user, PERSON_MANAGER_ROLES)
        person = self.find_by_id(person_id, current_user)
        self._repository.clear_faces_for_person(person.id)
        self._repository.delete(person)

    def list_media(
        self,
        person_id: str,
        current_user: AuthenticatedUser,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list, int]:
        person = self.find_by_id(person_id, current_user)
        return self._repository.list_media(
            person,
            page=page,
            page_size=page_size,
        )

    def link_media(
        self,
        person_id: str,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        self._require_roles(current_user, PERSON_MANAGER_ROLES)
        person = self.find_by_id(person_id, current_user)
        media = self._media_repository.find_by_id(media_id)

        if media is None:
            raise FotosMediaNotFoundError(media_id)

        if (
            media.organization_id != person.organization_id
            or media.tenant_id != person.tenant_id
            or media.environment_id != person.environment_id
        ):
            raise FotosPersonMediaScopeMismatchError()

        if self._repository.find_link(person_id, media_id):
            raise FotosPersonMediaAlreadyLinkedError()

        self._repository.add_link(
            FotosPersonMediaModel(
                person_id=person.id,
                media_id=media.id,
                organization_id=person.organization_id,
                tenant_id=person.tenant_id,
                environment_id=person.environment_id,
            )
        )

    def unlink_media(
        self,
        person_id: str,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        self._require_roles(current_user, PERSON_MANAGER_ROLES)
        self.find_by_id(person_id, current_user)
        link = self._repository.find_link(person_id, media_id)

        if link is None:
            raise FotosPersonMediaLinkNotFoundError()

        if self._repository.has_confirmed_face(person_id, media_id):
            raise ResourceConflictError(
                "Remova ou corrija os rostos confirmados antes de desvincular a mídia."
            )

        self._repository.delete_link(link)

    def _resolve_scope(
        self,
        environment_id: str,
    ) -> tuple[EnvironmentModel, TenantModel]:
        environment = self._environment_repository.find_by_id(environment_id)
        if environment is None:
            raise EnvironmentNotFoundError(environment_id)

        tenant = self._tenant_repository.find_by_id(environment.tenant_id)
        if tenant is None:
            raise TenantNotFoundError(environment.tenant_id)

        return environment, tenant

    def _require_scope(
        self,
        current_user: AuthenticatedUser,
        environment: EnvironmentModel,
        tenant: TenantModel,
    ) -> None:
        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )

    def _require_roles(
        self,
        current_user: AuthenticatedUser,
        roles: frozenset[UserModuleRole],
    ) -> None:
        self._authorization_service.require_module_roles(
            current_user,
            module_key=FOTOS_MODULE_KEY,
            allowed_roles=roles,
        )