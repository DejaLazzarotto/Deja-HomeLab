"""Dependência da curadoria facial."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from deja_indicadores_api.core.config import Settings, get_settings
from deja_indicadores_api.core.database import get_db_session
from deja_indicadores_api.fotos.curation.repository import FotosFaceRepository
from deja_indicadores_api.fotos.curation.service import FotosCurationService
from deja_indicadores_api.fotos.media.dependencies import (
    FotosMediaDerivativeServiceDependency,
    FotosMediaServiceDependency,
)
from deja_indicadores_api.fotos.people.dependencies import FotosPersonServiceDependency


def get_curation_service(
    session: Annotated[Session, Depends(get_db_session)],
    media: FotosMediaServiceDependency,
    people: FotosPersonServiceDependency,
    derivatives: FotosMediaDerivativeServiceDependency,
    settings: Annotated[Settings, Depends(get_settings)],
) -> FotosCurationService:
    return FotosCurationService(
        FotosFaceRepository(session), session, media, people, derivatives, settings
    )


CurationServiceDependency = Annotated[FotosCurationService, Depends(get_curation_service)]
