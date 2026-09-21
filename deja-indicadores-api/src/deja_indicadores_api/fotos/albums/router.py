from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from deja_indicadores_api.authentication.dependencies import require_roles
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.fotos.albums.dependencies import (
    FotosAlbumServiceDependency,
)
from deja_indicadores_api.fotos.albums.schemas import (
    FotosAlbumCreate,
    FotosAlbumPeriodDescriptionUpdate,
    FotosAlbumPeriodResponse,
    FotosAlbumResponse,
    FotosAlbumUpdate,
)
from deja_indicadores_api.module_management.dependencies import require_module
from deja_indicadores_api.user_management.models import UserRole

router = APIRouter(
    prefix="/fotos/albums",
    tags=["Deja Fotos - Álbuns"],
    dependencies=[
        Depends(require_module("fotos")),
    ],
)


FotosAlbumId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID do álbum.",
    ),
]

FotosAlbumPeriodYear = Annotated[
    int,
    Path(
        ge=1,
        le=9999,
        description="Ano original das mídias.",
    ),
]

FotosAlbumPeriodMonth = Annotated[
    int,
    Path(
        ge=1,
        le=12,
        description="Mês original das mídias.",
    ),
]

OrganizationFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra álbuns pela organização.",
    ),
]

TenantFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra álbuns pelo tenant.",
    ),
]

EnvironmentFilter = Annotated[
    str | None,
    Query(
        min_length=36,
        max_length=36,
        description="Filtra álbuns pelo ambiente.",
    ),
]

ActiveFilter = Annotated[
    bool | None,
    Query(
        description="Filtra álbuns pela situação ativa/inativa.",
    ),
]


FotosAlbumReader = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
            UserRole.VIEWER,
        )
    ),
]

FotosAlbumOperator = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
        )
    ),
]

FotosAlbumManager = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
        )
    ),
]


@router.get(
    "",
    response_model=list[FotosAlbumResponse],
)
def list_albums(
    service: FotosAlbumServiceDependency,
    current_user: FotosAlbumReader,
    organization_id: OrganizationFilter = None,
    tenant_id: TenantFilter = None,
    environment_id: EnvironmentFilter = None,
    active: ActiveFilter = None,
) -> list[FotosAlbumResponse]:
    """Lista álbuns dentro do escopo permitido."""

    return service.list(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        active=active,
    )


@router.get(
    "/{album_id}/periods",
    response_model=list[FotosAlbumPeriodResponse],
)
def list_album_periods(
    album_id: FotosAlbumId,
    service: FotosAlbumServiceDependency,
    current_user: FotosAlbumReader,
) -> list[FotosAlbumPeriodResponse]:
    """Lista os períodos reais existentes em um álbum."""

    return service.list_periods(
        album_id,
        current_user,
    )


@router.put(
    "/{album_id}/periods/{year}/{month}",
    response_model=FotosAlbumPeriodResponse,
)
def update_album_period_description(
    album_id: FotosAlbumId,
    year: FotosAlbumPeriodYear,
    month: FotosAlbumPeriodMonth,
    input_data: FotosAlbumPeriodDescriptionUpdate,
    service: FotosAlbumServiceDependency,
    current_user: FotosAlbumOperator,
) -> FotosAlbumPeriodResponse:
    """Salva ou remove a descrição mensal de um álbum."""

    return service.update_period_description(
        album_id,
        year,
        month,
        input_data,
        current_user,
    )


@router.get(
    "/{album_id}",
    response_model=FotosAlbumResponse,
)
def get_album(
    album_id: FotosAlbumId,
    service: FotosAlbumServiceDependency,
    current_user: FotosAlbumReader,
) -> FotosAlbumResponse:
    """Retorna um álbum específico."""

    return service.find_by_id(
        album_id,
        current_user,
    )


@router.post(
    "",
    response_model=FotosAlbumResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_album(
    input_data: FotosAlbumCreate,
    service: FotosAlbumServiceDependency,
    current_user: FotosAlbumOperator,
) -> FotosAlbumResponse:
    """Cria um álbum no escopo permitido."""

    return service.create(
        input_data,
        current_user,
    )


@router.put(
    "/{album_id}",
    response_model=FotosAlbumResponse,
)
def update_album(
    album_id: FotosAlbumId,
    input_data: FotosAlbumUpdate,
    service: FotosAlbumServiceDependency,
    current_user: FotosAlbumOperator,
) -> FotosAlbumResponse:
    """Atualiza integralmente um álbum."""

    return service.update(
        album_id,
        input_data,
        current_user,
    )


@router.delete(
    "/{album_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_album(
    album_id: FotosAlbumId,
    service: FotosAlbumServiceDependency,
    current_user: FotosAlbumManager,
) -> Response:
    """Exclui um álbum vazio."""

    service.delete(
        album_id,
        current_user,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )