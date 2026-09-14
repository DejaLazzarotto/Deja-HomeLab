from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.core.database import (
    get_db_session,
)
from deja_indicadores_api.fotos.albums.repository import (
    FotosAlbumRepository,
)
from deja_indicadores_api.fotos.albums.service import (
    FotosAlbumService,
)
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)


def get_fotos_album_service(
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
) -> FotosAlbumService:
    """Monta o serviço de álbuns do Deja Fotos."""

    return FotosAlbumService(
        repository=FotosAlbumRepository(session),
        tenant_repository=TenantRepository(session),
        environment_repository=EnvironmentRepository(session),
        authorization_service=AuthorizationService(),
    )


FotosAlbumServiceDependency = Annotated[
    FotosAlbumService,
    Depends(get_fotos_album_service),
]