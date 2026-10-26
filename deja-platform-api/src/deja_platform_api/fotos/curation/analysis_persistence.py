"""Persistência transacional de resultados da análise facial automática."""

from uuid import uuid4

from sqlalchemy.orm import Session

from deja_platform_api.fotos.curation.analysis_models import FaceAnalysisResult
from deja_platform_api.fotos.curation.job_repository import FotosFaceJobRepository
from deja_platform_api.fotos.curation.models import FotosFaceModel
from deja_platform_api.fotos.curation.repository import FotosFaceRepository
from deja_platform_api.fotos.curation.service import same_face_box
from deja_platform_api.fotos.media.models import FotosMediaModel
from deja_platform_api.fotos.people.models import FotosPersonModel


def persist_face_analysis(
    session: Session,
    job_id: str,
    claim_token: str,
    analysis: FaceAnalysisResult,
) -> int:
    """Grava resultados somente quando a reserva e o ambiente são válidos.

    O chamador é responsável por confirmar ou reverter a transação.
    """

    jobs = FotosFaceJobRepository(session)
    job = jobs.lock_valid_claim(job_id, claim_token)

    media = session.get(FotosMediaModel, job.media_id)

    if media is None:
        raise RuntimeError("Fotografia não encontrada.")

    expected_scope = (
        job.organization_id,
        job.tenant_id,
        job.environment_id,
    )

    media_scope = (
        media.organization_id,
        media.tenant_id,
        media.environment_id,
    )

    analysis_scope = (
        analysis.organization_id,
        analysis.tenant_id,
        analysis.environment_id,
    )

    if (
        media.id != analysis.media_id
        or media_scope != expected_scope
        or analysis_scope != expected_scope
    ):
        raise RuntimeError("Ambiente da análise facial inválido.")

    if (
        media.media_type != "image"
        or media.processing_status != "ready"
        or media.deleted_at is not None
    ):
        raise RuntimeError("A fotografia não está disponível para análise.")

    faces = FotosFaceRepository(session)
    existing = faces.all_for_media(media.id, media.environment_id)

    created = 0

    for detection in analysis.detections:
        box = (
            detection.x,
            detection.y,
            detection.width,
            detection.height,
        )

        if any(same_face_box(face, box) for face in existing):
            continue

        person_id = None
        confidence = None

        if detection.person_id:
            person = session.get(FotosPersonModel, detection.person_id)

            if (
                person is not None
                and person.active
                and (
                    person.organization_id,
                    person.tenant_id,
                    person.environment_id,
                )
                == expected_scope
            ):
                person_id = person.id
                confidence = detection.confidence

        face = FotosFaceModel(
            id=str(uuid4()),
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            x=detection.x,
            y=detection.y,
            width=detection.width,
            height=detection.height,
            origin="detected",
            status="suggested" if person_id else "unknown",
            person_id=person_id,
            confidence=confidence,
        )

        faces.stage(face)
        existing.append(face)
        created += 1

    jobs.complete(job, claim_token)

    return created
