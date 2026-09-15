from collections.abc import Callable

from sqlalchemy.orm import Session

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.fotos.media.derivative_repository import (
    FotosMediaDerivativeRepository,
)
from deja_indicadores_api.fotos.media.derivative_service import (
    FotosMediaDerivativeService,
)
from deja_indicadores_api.fotos.media.repository import (
    FotosMediaRepository,
)

SessionFactory = Callable[[], Session]


def process_media_in_background(
    media_id: str,
    *,
    session_factory: SessionFactory,
    settings: Settings,
) -> None:
    """Processa derivados usando uma sessão independente da requisição HTTP."""

    with session_factory() as session:
        media_repository = FotosMediaRepository(session)

        media = media_repository.find_by_id(media_id)

        if media is None:
            return

        derivative_service = FotosMediaDerivativeService(
            media_repository,
            FotosMediaDerivativeRepository(session),
            settings,
        )

        if media.media_type == "image":
            derivative_service.process_image(media)
        elif media.media_type == "video":
            derivative_service.process_video(media)
        else:
            raise ValueError(
                "Tipo de mídia não suportado para processamento."
            )