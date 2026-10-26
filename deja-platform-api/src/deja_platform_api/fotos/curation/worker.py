"""Execução sequencial de trabalhos de reconhecimento facial."""

import logging
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_platform_api.fotos.curation.analysis_models import FaceAnalysisResult
from deja_platform_api.fotos.curation.analysis_persistence import persist_face_analysis
from deja_platform_api.fotos.curation.analyzer import analyze_faces
from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
from deja_platform_api.fotos.curation.job_repository import FotosFaceJobRepository
from deja_platform_api.fotos.curation.models import FotosFaceReferenceModel
from deja_platform_api.fotos.media.models import FotosMediaModel
from deja_platform_api.fotos.people.models import FotosPersonModel

logger = logging.getLogger(__name__)


def process_next_face_job(
    session_factory: Callable[[], Session],
    resolve_image_path: Callable[[FotosMediaModel], Path],
    uploads_dir: Path,
    models_dir: Path,
) -> bool:
    """Processa um trabalho, retornando False quando a fila está vazia."""

    with session_factory() as session:
        jobs = FotosFaceJobRepository(session)
        job = jobs.claim_next()

        if job is None:
            session.rollback()
            return False

        job_id = job.id
        media_id = job.media_id
        claim_token = job.claim_token

        if claim_token is None:
            session.rollback()
            raise RuntimeError("Trabalho reservado sem claim_token.")

        session.commit()

    try:
        with session_factory() as session:
            media = session.get(FotosMediaModel, media_id)

            if media is None:
                raise RuntimeError("Fotografia não encontrada.")

            scope = (
                media.organization_id,
                media.tenant_id,
                media.environment_id,
            )

            references = session.execute(
                select(
                    FotosFaceReferenceModel.person_id,
                    FotosFaceReferenceModel.storage_key,
                )
                .join(
                    FotosPersonModel,
                    FotosFaceReferenceModel.person_id == FotosPersonModel.id,
                )
                .where(
                    FotosFaceReferenceModel.organization_id == scope[0],
                    FotosFaceReferenceModel.tenant_id == scope[1],
                    FotosFaceReferenceModel.environment_id == scope[2],
                    FotosPersonModel.organization_id == scope[0],
                    FotosPersonModel.tenant_id == scope[1],
                    FotosPersonModel.environment_id == scope[2],
                    FotosPersonModel.active.is_(True),
                )
            ).all()

            reference_files = [
                (person_id, uploads_dir / storage_key) for person_id, storage_key in references
            ]

            image_path = resolve_image_path(media)

            analysis: FaceAnalysisResult = analyze_faces(
                media,
                image_path,
                reference_files,
                models_dir,
            )

            session.rollback()

        with session_factory() as session:
            persist_face_analysis(
                session,
                job_id,
                claim_token,
                analysis,
            )
            session.commit()

    except Exception as exc:
        logger.exception(
            "Falha no reconhecimento facial: job_id=%s media_id=%s",
            job_id,
            media_id,
        )

        with session_factory() as session:
            jobs = FotosFaceJobRepository(session)
            job = session.get(FotosFaceJobModel, job_id)

            if job is None:
                logger.warning(
                    "Trabalho facial inexistente ao registrar falha: %s",
                    job_id,
                )
            else:
                try:
                    jobs.fail(job, claim_token, str(exc))
                    session.commit()
                except RuntimeError:
                    session.rollback()
                    logger.warning(
                        "Reserva facial expirada ou inválida: job_id=%s",
                        job_id,
                    )

    return True
