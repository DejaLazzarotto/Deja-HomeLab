import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from deja_platform_api.core.config import Settings
from deja_platform_api.fotos.curation.job_repository import FotosFaceJobRepository
from deja_platform_api.fotos.media.derivative_repository import (
    FotosMediaDerivativeRepository,
)
from deja_platform_api.fotos.media.derivative_service import (
    FotosMediaDerivativeService,
)
from deja_platform_api.fotos.media.repository import (
    FotosMediaRepository,
)

logger = logging.getLogger(__name__)

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

        derivative_service.process(media)

        # Enfileirar somente fotografias concluídas com sucesso.
        if (
            media.media_type == "image"
            and media.processing_status == "ready"
            and media.deleted_at is None
        ):
            try:
                face_jobs = FotosFaceJobRepository(session)
                face_jobs.enqueue(media)
                session.commit()
            except Exception:
                session.rollback()
                logger.exception(
                    "Falha ao enfileirar reconhecimento facial: media_id=%s",
                    media.id,
                )
