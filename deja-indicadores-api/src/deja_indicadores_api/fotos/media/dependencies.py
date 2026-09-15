from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.core.config import Settings, get_settings
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.fotos.albums.repository import (
    FotosAlbumRepository,
)
from deja_indicadores_api.fotos.media.repository import (
    FotosMediaRepository,
)
from deja_indicadores_api.fotos.media.service import (
    FotosMediaService,
)
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]

SettingsDependency = Annotated[
    Settings,
    Depends(get_settings),
]


def get_fotos_media_service(
    session: DatabaseSession,
    settings: SettingsDependency,
) -> FotosMediaService:
    """Cria o serviço de mídias para a sessão da requisição."""

    return FotosMediaService(
        FotosMediaRepository(session),
        FotosAlbumRepository(session),
        TenantRepository(session),
        EnvironmentRepository(session),
        AuthorizationService(),
        settings,
    )


FotosMediaServiceDependency = Annotated[
    FotosMediaService,
    Depends(get_fotos_media_service),
]