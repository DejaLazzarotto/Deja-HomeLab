from uuid import uuid4

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.fotos.albums.exceptions import (
    FotosAlbumAlreadyExistsError,
    FotosAlbumHasMediaError,
    FotosAlbumNotFoundError,
    FotosAlbumPeriodNotFoundError,
)
from deja_indicadores_api.fotos.albums.models import (
    FotosAlbumModel,
    FotosAlbumPeriodDescriptionModel,
)
from deja_indicadores_api.fotos.albums.repository import (
    FotosAlbumPeriodRow,
    FotosAlbumRepository,
)
from deja_indicadores_api.fotos.albums.schemas import (
    FotosAlbumCreate,
    FotosAlbumPeriodDescriptionUpdate,
    FotosAlbumPeriodResponse,
    FotosAlbumUpdate,
)
from deja_indicadores_api.fotos.media.repository import (
    FotosMediaRepository,
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
from deja_indicadores_api.user_management.models import (
    UserRole,
)

FOTOS_ALBUM_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)

FOTOS_ALBUM_OPERATOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
    }
)

FOTOS_ALBUM_MANAGER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
    }
)


class FotosAlbumService:
    """Regras de aplicação dos álbuns do Deja Fotos."""

    def __init__(
        self,
        repository: FotosAlbumRepository,
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
    ) -> list[FotosAlbumModel]:
        """Lista álbuns dentro do escopo permitido."""

        self._require_roles(
            current_user,
            FOTOS_ALBUM_READER_ROLES,
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
            active=active,
        )

    def find_by_id(
        self,
        album_id: str,
        current_user: AuthenticatedUser,
    ) -> FotosAlbumModel:
        """Retorna um álbum dentro do escopo permitido."""

        self._require_roles(
            current_user,
            FOTOS_ALBUM_READER_ROLES,
        )

        album = self._find_by_id(album_id)

        environment, tenant = self._resolve_album_scope(
            album,
        )

        self._require_album_scope(
            current_user,
            environment,
            tenant,
        )

        return album

    def list_periods(
        self,
        album_id: str,
        current_user: AuthenticatedUser,
    ) -> list[FotosAlbumPeriodResponse]:
        """Lista os períodos reais de um álbum autorizado."""

        self._require_roles(
            current_user,
            FOTOS_ALBUM_READER_ROLES,
        )

        album = self._find_by_id(
            album_id,
        )

        environment, tenant = self._resolve_album_scope(
            album,
        )

        self._require_album_scope(
            current_user,
            environment,
            tenant,
        )

        return [
            FotosAlbumPeriodResponse(
                year=year,
                month=month,
                media_count=media_count,
                description=description,
            )
            for (
                year,
                month,
                media_count,
                description,
            ) in self._repository.list_periods(
                album.id,
            )
        ]

    def create(
        self,
        input_data: FotosAlbumCreate,
        current_user: AuthenticatedUser,
    ) -> FotosAlbumModel:
        """Cadastra um álbum dentro do escopo permitido."""

        self._require_roles(
            current_user,
            FOTOS_ALBUM_OPERATOR_ROLES,
        )

        environment = self._require_environment(
            input_data.environment_id,
        )

        tenant = self._require_tenant(
            environment.tenant_id,
        )

        self._require_album_scope(
            current_user,
            environment,
            tenant,
        )

        existing_album = self._repository.find_by_scope_and_name(
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
            name=input_data.name,
        )

        if existing_album is not None:
            raise FotosAlbumAlreadyExistsError(
                input_data.name,
            )

        album = FotosAlbumModel(
            id=str(uuid4()),
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
            name=input_data.name,
            description=input_data.description,
            active=input_data.active,
        )

        return self._repository.add(
            album,
        )

    def update(
        self,
        album_id: str,
        input_data: FotosAlbumUpdate,
        current_user: AuthenticatedUser,
    ) -> FotosAlbumModel:
        """Atualiza um álbum dentro do escopo permitido."""

        self._require_roles(
            current_user,
            FOTOS_ALBUM_OPERATOR_ROLES,
        )

        album = self._find_by_id(
            album_id,
        )

        current_environment, current_tenant = (
            self._resolve_album_scope(
                album,
            )
        )

        self._require_album_scope(
            current_user,
            current_environment,
            current_tenant,
        )

        target_environment = self._require_environment(
            input_data.environment_id,
        )

        target_tenant = self._require_tenant(
            target_environment.tenant_id,
        )

        self._require_album_scope(
            current_user,
            target_environment,
            target_tenant,
        )

        existing_album = self._repository.find_by_scope_and_name(
            organization_id=target_tenant.organization_id,
            tenant_id=target_tenant.id,
            environment_id=target_environment.id,
            name=input_data.name,
        )

        if (
            existing_album is not None
            and existing_album.id != album_id
        ):
            raise FotosAlbumAlreadyExistsError(
                input_data.name,
            )

        album.organization_id = (
            target_tenant.organization_id
        )
        album.tenant_id = target_tenant.id
        album.environment_id = target_environment.id
        album.name = input_data.name
        album.description = input_data.description
        album.active = input_data.active

        return self._repository.update(
            album,
        )

    def update_period_description(
        self,
        album_id: str,
        year: int,
        month: int,
        input_data: FotosAlbumPeriodDescriptionUpdate,
        current_user: AuthenticatedUser,
    ) -> FotosAlbumPeriodResponse:
        """Salva ou remove a descrição de um período real do álbum."""

        self._require_roles(
            current_user,
            FOTOS_ALBUM_OPERATOR_ROLES,
        )

        album = self._find_by_id(
            album_id,
        )

        environment, tenant = self._resolve_album_scope(
            album,
        )

        self._require_album_scope(
            current_user,
            environment,
            tenant,
        )

        period = self._find_period(
            album.id,
            year,
            month,
        )

        period_description = (
            self._repository.find_period_description(
                album_id=album.id,
                year=year,
                month=month,
            )
        )

        if input_data.description is None:
            if period_description is not None:
                self._repository.delete_period_description(
                    period_description,
                )
        else:
            if period_description is None:
                period_description = (
                    FotosAlbumPeriodDescriptionModel(
                        id=str(uuid4()),
                        organization_id=album.organization_id,
                        tenant_id=album.tenant_id,
                        environment_id=album.environment_id,
                        album_id=album.id,
                        original_year=year,
                        original_month=month,
                        description=input_data.description,
                    )
                )
            else:
                period_description.description = (
                    input_data.description
                )

            self._repository.save_period_description(
                period_description,
            )

        return FotosAlbumPeriodResponse(
            year=year,
            month=month,
            media_count=period[2],
            description=input_data.description,
        )

    def delete(
        self,
        album_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exclui um álbum vazio dentro do escopo permitido."""

        self._require_roles(
            current_user,
            FOTOS_ALBUM_MANAGER_ROLES,
        )

        album = self._find_by_id(
            album_id,
        )

        environment, tenant = self._resolve_album_scope(
            album,
        )

        self._require_album_scope(
            current_user,
            environment,
            tenant,
        )

        if self._media_repository.exists_by_album_id(
            album.id,
        ):
            raise FotosAlbumHasMediaError(
                album.id,
            )

        self._repository.delete(
            album,
        )

    def _find_by_id(
        self,
        album_id: str,
    ) -> FotosAlbumModel:
        album = self._repository.find_by_id(
            album_id,
        )

        if album is None:
            raise FotosAlbumNotFoundError(
                album_id,
            )

        return album

    def _find_period(
        self,
        album_id: str,
        year: int,
        month: int,
    ) -> FotosAlbumPeriodRow:
        for period in self._repository.list_periods(
            album_id,
        ):
            if (
                period[0] == year
                and period[1] == month
            ):
                return period

        raise FotosAlbumPeriodNotFoundError(
            album_id,
            year,
            month,
        )

    def _require_environment(
        self,
        environment_id: str,
    ) -> EnvironmentModel:
        environment = (
            self._environment_repository.find_by_id(
                environment_id,
            )
        )

        if environment is None:
            raise EnvironmentNotFoundError(
                environment_id,
            )

        return environment

    def _require_tenant(
        self,
        tenant_id: str,
    ) -> TenantModel:
        tenant = self._tenant_repository.find_by_id(
            tenant_id,
        )

        if tenant is None:
            raise TenantNotFoundError(
                tenant_id,
            )

        return tenant

    def _resolve_album_scope(
        self,
        album: FotosAlbumModel,
    ) -> tuple[
        EnvironmentModel,
        TenantModel,
    ]:
        """Resolve a hierarquia institucional real do álbum."""

        environment = self._require_environment(
            album.environment_id,
        )

        tenant = self._require_tenant(
            environment.tenant_id,
        )

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

    def _require_album_scope(
        self,
        current_user: AuthenticatedUser,
        environment: EnvironmentModel,
        tenant: TenantModel,
    ) -> None:
        """Exige acesso à hierarquia institucional do álbum."""

        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )