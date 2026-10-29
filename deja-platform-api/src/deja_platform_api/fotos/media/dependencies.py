from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_platform_api.authentication.authorization import (
    AuthorizationService,
)
from deja_platform_api.core.config import Settings, get_settings
from deja_platform_api.core.database import (
    SessionLocal,
    get_db_session,
)
from deja_platform_api.fotos.curation.repository import FotosFaceRepository
from deja_platform_api.fotos.albums.repository import (
    FotosAlbumRepository,
)
from deja_platform_api.fotos.media.derivative_repository import (
    FotosMediaDerivativeRepository,
)
from deja_platform_api.fotos.media.derivative_service import (
    FotosMediaDerivativeService,
)
from deja_platform_api.fotos.media.repository import (
    FotosMediaRepository,
)
from deja_platform_api.fotos.media.service import (
    FotosMediaService,
)
from deja_platform_api.tenant_management.repository import (
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

FotosMediaSessionFactory = Callable[[], Session]


def get_fotos_media_session_factory() -> FotosMediaSessionFactory:
    """Fornece a fábrica de sessões para processamento independente."""

    return SessionLocal


FotosMediaSessionFactoryDependency = Annotated[
    FotosMediaSessionFactory,
    Depends(get_fotos_media_session_factory),
]


def get_fotos_media_service(
    session: DatabaseSession,
    settings: SettingsDependency,
) -> FotosMediaService:
    """Cria o serviço de mídias para a sessão da requisição."""

    return FotosMediaService(
        FotosMediaRepository(session),
        FotosAlbumRepository(session),
        FotosMediaDerivativeRepository(session),
        TenantRepository(session),
        EnvironmentRepository(session),
        AuthorizationService(),
        settings,
        FotosFaceRepository(session),
    )


FotosMediaServiceDependency = Annotated[
    FotosMediaService,
    Depends(get_fotos_media_service),
]


def get_fotos_media_derivative_service(
    session: DatabaseSession,
    settings: SettingsDependency,
) -> FotosMediaDerivativeService:
    """Cria o serviço de derivados para a sessão da requisição."""

    return FotosMediaDerivativeService(
        FotosMediaRepository(session),
        FotosMediaDerivativeRepository(session),
        settings,
    )


FotosMediaDerivativeServiceDependency = Annotated[
    FotosMediaDerivativeService,
    Depends(get_fotos_media_derivative_service),
]
