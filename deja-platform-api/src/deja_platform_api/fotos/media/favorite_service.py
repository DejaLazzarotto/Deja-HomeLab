"""Regras de aplicação dos favoritos individuais do Deja Fotos."""

from uuid import uuid4

from deja_platform_api.authentication.authorization import (
    AuthorizationService,
)
from deja_platform_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_platform_api.fotos.media.favorite_models import (
    FotosMediaFavoriteModel,
)
from deja_platform_api.fotos.media.favorite_repository import (
    FotosMediaFavoriteRepository,
)
from deja_platform_api.fotos.media.models import (
    FotosMediaModel,
)
from deja_platform_api.fotos.media.service import (
    FOTOS_MEDIA_READER_ROLES,
    FotosMediaService,
)


class FotosMediaFavoriteService:
    """Gerencia favoritos respeitando usuário e escopo institucional."""

    def __init__(
        self,
        repository: FotosMediaFavoriteRepository,
        media_service: FotosMediaService,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._media_service = media_service
        self._authorization_service = authorization_service

    def _require_reader(
        self,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exige autorização de leitura no módulo Fotos."""

        self._authorization_service.require_module_roles(
            current_user,
            module_key="fotos",
            allowed_roles=FOTOS_MEDIA_READER_ROLES,
        )

    def is_favorite(
        self,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> bool:
        """Consulta o favorito somente após validar acesso à mídia."""

        self._require_reader(current_user)

        self._media_service.find_by_id(
            media_id,
            current_user,
        )

        return self._repository.exists(
            current_user.id,
            media_id,
        )

    def add(
        self,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> FotosMediaFavoriteModel:
        """Marca uma mídia autorizada como favorita."""

        self._require_reader(current_user)

        self._media_service.find_by_id(
            media_id,
            current_user,
        )

        favorite = FotosMediaFavoriteModel(
            id=str(uuid4()),
            user_id=current_user.id,
            media_id=media_id,
        )

        return self._repository.add(favorite)

    def remove(
        self,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> bool:
        """Remove somente o favorito do usuário autenticado."""

        self._require_reader(current_user)

        self._media_service.find_by_id(
            media_id,
            current_user,
        )

        return self._repository.remove(
            current_user.id,
            media_id,
        )

    def list(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        page: int = 1,
        page_size: int = 30,
    ) -> tuple[list[FotosMediaModel], int]:
        """Lista favoritos dentro do escopo institucional autorizado."""

        self._require_reader(current_user)

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
            current_user.id,
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
            page=page,
            page_size=page_size,
        )