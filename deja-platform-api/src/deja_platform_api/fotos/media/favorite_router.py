"""Endpoints de favoritos individuais do Deja Fotos."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from fastapi import status as http_status
from pydantic import BaseModel

from deja_platform_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_platform_api.fotos.media.favorite_dependencies import (
    FotosMediaFavoriteServiceDependency,
)
from deja_platform_api.fotos.media.schemas import (
    FotosMediaListResponse,
)
from deja_platform_api.module_management.dependencies import (
    require_module,
    require_module_roles,
)
from deja_platform_api.user_management.models import (
    UserModuleRole,
)

router = APIRouter(
    prefix="/fotos/favorites",
    tags=["Deja Fotos - Favoritos"],
    dependencies=[Depends(require_module("fotos"))],
)


FotosFavoriteReader = Annotated[
    AuthenticatedUser,
    Depends(
        require_module_roles(
            "fotos",
            UserModuleRole.MANAGER,
            UserModuleRole.VIEWER,
        )
    ),
]


FavoriteMediaId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID da mídia.",
    ),
]


class FotosFavoriteStatusResponse(BaseModel):
    """Estado de favorito de uma mídia para o usuário autenticado."""

    media_id: str
    is_favorite: bool


@router.get(
    "",
    response_model=FotosMediaListResponse,
)
def list_favorites(
    service: FotosMediaFavoriteServiceDependency,
    current_user: FotosFavoriteReader,
    organization_id: str | None = Query(default=None),
    tenant_id: str | None = Query(default=None),
    environment_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=200),
) -> FotosMediaListResponse:
    """Lista mídias favoritas do usuário dentro do escopo autorizado."""

    items, total = service.list(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        page=page,
        page_size=page_size,
    )

    return FotosMediaListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/{media_id}",
    response_model=FotosFavoriteStatusResponse,
)
def get_favorite_status(
    media_id: FavoriteMediaId,
    service: FotosMediaFavoriteServiceDependency,
    current_user: FotosFavoriteReader,
) -> FotosFavoriteStatusResponse:
    """Consulta se a mídia está nos favoritos do usuário."""

    return FotosFavoriteStatusResponse(
        media_id=media_id,
        is_favorite=service.is_favorite(
            media_id,
            current_user,
        ),
    )


@router.put(
    "/{media_id}",
    response_model=FotosFavoriteStatusResponse,
)
def add_favorite(
    media_id: FavoriteMediaId,
    service: FotosMediaFavoriteServiceDependency,
    current_user: FotosFavoriteReader,
) -> FotosFavoriteStatusResponse:
    """Marca uma mídia autorizada como favorita."""

    service.add(
        media_id,
        current_user,
    )

    return FotosFavoriteStatusResponse(
        media_id=media_id,
        is_favorite=True,
    )


@router.delete(
    "/{media_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
def remove_favorite(
    media_id: FavoriteMediaId,
    service: FotosMediaFavoriteServiceDependency,
    current_user: FotosFavoriteReader,
) -> None:
    """Remove o favorito pertencente ao usuário autenticado."""

    service.remove(
        media_id,
        current_user,
    )