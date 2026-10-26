"""Executor independente da fila de reconhecimento facial do VIVARO."""

import logging
import time

from deja_platform_api.core.config import get_settings
from deja_platform_api.core.database import SessionLocal
from deja_platform_api.fotos.curation.job_repository import FotosFaceJobRepository
from deja_platform_api.fotos.curation.worker import process_next_face_job
from deja_platform_api.fotos.media.derivative_repository import (
    FotosMediaDerivativeRepository,
)
from deja_platform_api.fotos.media.models import FotosMediaModel

logger = logging.getLogger(__name__)


def resolve_preview_path(media: FotosMediaModel):
    """Localiza o preview da fotografia cadastrada."""

    settings = get_settings()

    with SessionLocal() as session:
        repository = FotosMediaDerivativeRepository(session)
        derivative = repository.find_by_media_and_type(media.id, "preview")

        if derivative is None:
            raise FileNotFoundError(f"Preview não encontrado para fotografia {media.id}.")

        uploads_root = settings.uploads_dir.resolve()
        path = (uploads_root / derivative.storage_key).resolve()

        if not path.is_relative_to(uploads_root):
            raise ValueError(f"Caminho de preview fora do diretório autorizado: {media.id}.")

        if not path.is_file():
            raise FileNotFoundError(f"Arquivo de preview inexistente: {media.id}.")

        return path


def run_worker_cycle(settings) -> bool:
    """Recupera tarefas interrompidas e processa no máximo uma fotografia."""

    with SessionLocal() as session:
        recovered = FotosFaceJobRepository(session).recover_stale()
        session.commit()

        if recovered:
            logger.warning(
                "Trabalhos faciais recuperados: %s",
                recovered,
            )

    return process_next_face_job(
        session_factory=SessionLocal,
        resolve_image_path=resolve_preview_path,
        uploads_dir=settings.uploads_dir,
        models_dir=settings.fotos_face_models_dir,
    )


def run_worker() -> None:
    """Consome sequencialmente os trabalhos da fila facial."""

    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    logger.info("Worker facial VIVARO iniciado.")

    while True:
        try:
            processed = run_worker_cycle(settings)

            if not processed:
                time.sleep(5)

        except KeyboardInterrupt:
            logger.info("Worker facial interrompido.")
            break

        except Exception:
            logger.exception("Erro inesperado no worker facial.")
            time.sleep(10)


if __name__ == "__main__":
    run_worker()
