"""Dependências FastAPI para Favoritos do Deja Fotos."""

from typing import Annotated

from fastapi import Depends

from deja_platform_api.authentication.authorization import (
    AuthorizationService,
)
from deja_platform_api.fotos.media.dependencies import (
    DatabaseSession,
    FotosMediaServiceDependency,
)
from deja_platform_api.fotos.media.favorite_repository import (
    FotosMediaFavoriteRepository,
)
from deja_platform_api.fotos.media.favorite_service import (
    FotosMediaFavoriteService,
)


def get_fotos_media_favorite_service(
    session: DatabaseSession,
    media_service: FotosMediaServiceDependency,
) -> FotosMediaFavoriteService:
    """Cria o serviço de Favoritos para a sessão da requisição."""

    return FotosMediaFavoriteService(
        FotosMediaFavoriteRepository(session),
        media_service,
        AuthorizationService(),
    )


FotosMediaFavoriteServiceDependency = Annotated[
    FotosMediaFavoriteService,
    Depends(get_fotos_media_favorite_service),
]