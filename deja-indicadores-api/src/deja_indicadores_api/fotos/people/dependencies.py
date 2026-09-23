"""Dependências dos serviços de Pessoas do Deja Fotos."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.core.config import Settings, get_settings
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.fotos.media.repository import (
    FotosMediaRepository,
)
from deja_indicadores_api.fotos.people.avatar import (
    FotosPersonAvatarService,
)
from deja_indicadores_api.fotos.people.repository import (
    FotosPersonRepository,
)
from deja_indicadores_api.fotos.people.service import (
    FotosPersonService,
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


def get_fotos_person_service(
    session: DatabaseSession,
) -> FotosPersonService:
    """Monta o serviço com repositórios da mesma sessão."""

    return FotosPersonService(
        repository=FotosPersonRepository(session),
        media_repository=FotosMediaRepository(session),
        tenant_repository=TenantRepository(session),
        environment_repository=EnvironmentRepository(session),
        authorization_service=AuthorizationService(),
    )


FotosPersonServiceDependency = Annotated[
    FotosPersonService,
    Depends(get_fotos_person_service),
]


def get_fotos_person_avatar_service(
    session: DatabaseSession,
    settings: SettingsDependency,
    person_service: FotosPersonServiceDependency,
) -> FotosPersonAvatarService:
    """Monta o serviço de avatar no armazenamento existente."""

    return FotosPersonAvatarService(
        person_service=person_service,
        repository=FotosPersonRepository(session),
        authorization_service=AuthorizationService(),
        settings=settings,
    )


FotosPersonAvatarServiceDependency = Annotated[
    FotosPersonAvatarService,
    Depends(get_fotos_person_avatar_service),
]