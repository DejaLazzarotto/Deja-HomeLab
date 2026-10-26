"""Testes da persistência transacional do reconhecimento facial."""

import pytest
from sqlalchemy import func, select

from deja_platform_api.fotos.curation.analysis_models import (
    FaceAnalysisResult,
    FaceDetectionResult,
)
from deja_platform_api.fotos.curation.analysis_persistence import (
    persist_face_analysis,
)
from deja_platform_api.fotos.curation.job_repository import (
    FotosFaceJobRepository,
)
from deja_platform_api.fotos.curation.models import FotosFaceModel
from deja_platform_api.fotos.media.models import FotosMediaModel

pytest_plugins = ("tests.fotos.media.test_favorite_repository",)


def test_invalid_claim_does_not_create_faces(
    favorite_media_context,
) -> None:
    """Uma reserva inválida não pode registrar rostos."""

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"
        session.commit()

        jobs = FotosFaceJobRepository(session)
        job = jobs.enqueue(media)
        assert job is not None
        session.commit()

        claimed = jobs.claim_next()
        assert claimed is not None
        session.commit()

        analysis = FaceAnalysisResult(
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            detections=(
                FaceDetectionResult(
                    x=0.1,
                    y=0.2,
                    width=0.3,
                    height=0.4,
                ),
            ),
        )

        with pytest.raises(RuntimeError, match="Reserva facial inválida"):
            persist_face_analysis(
                session,
                job.id,
                "token-invalido",
                analysis,
            )

        session.rollback()

        total = session.scalar(
            select(func.count(FotosFaceModel.id)).where(FotosFaceModel.media_id == media.id)
        )

        assert total == 0


def test_face_analysis_rejects_different_organization(
    favorite_media_context,
) -> None:
    """Resultados de outra organização não podem ser gravados."""

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"
        session.commit()

        jobs = FotosFaceJobRepository(session)
        job = jobs.enqueue(media)
        assert job is not None
        session.commit()

        claimed = jobs.claim_next()
        assert claimed is not None

        token = claimed.claim_token
        assert token is not None
        session.commit()

        analysis = FaceAnalysisResult(
            media_id=media.id,
            organization_id="outra-organizacao",
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            detections=(
                FaceDetectionResult(
                    x=0.1,
                    y=0.2,
                    width=0.3,
                    height=0.4,
                ),
            ),
        )

        with pytest.raises(
            RuntimeError,
            match="Ambiente da análise facial inválido",
        ):
            persist_face_analysis(
                session,
                job.id,
                token,
                analysis,
            )

        session.rollback()

        total = session.scalar(
            select(func.count(FotosFaceModel.id)).where(FotosFaceModel.media_id == media.id)
        )

        assert total == 0


def test_face_analysis_preserves_confirmed_face(
    favorite_media_context,
) -> None:
    """A análise automática não altera rostos confirmados manualmente."""

    from uuid import uuid4

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"
        session.commit()

        existing_face = FotosFaceModel(
            id=str(uuid4()),
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            x=0.1,
            y=0.2,
            width=0.3,
            height=0.4,
            origin="manual",
            status="confirmed",
            person_id=None,
        )

        session.add(existing_face)
        session.commit()

        jobs = FotosFaceJobRepository(session)
        job = jobs.enqueue(media)
        assert job is not None
        session.commit()

        claimed = jobs.claim_next()
        assert claimed is not None

        token = claimed.claim_token
        assert token is not None
        session.commit()

        analysis = FaceAnalysisResult(
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            detections=(
                FaceDetectionResult(
                    x=0.1,
                    y=0.2,
                    width=0.3,
                    height=0.4,
                ),
            ),
        )

        created = persist_face_analysis(
            session,
            job.id,
            token,
            analysis,
        )
        session.commit()
        session.expire_all()

        current = session.get(FotosFaceModel, existing_face.id)

        assert created == 0
        assert current is not None
        assert current.status == "confirmed"
        assert current.origin == "manual"

        total = session.scalar(
            select(func.count(FotosFaceModel.id)).where(FotosFaceModel.media_id == media.id)
        )

        assert total == 1


def test_face_analysis_rejects_nonexistent_person(
    favorite_media_context,
) -> None:
    """Uma identidade inexistente não pode ser aceita como sugestão."""

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"
        session.commit()

        jobs = FotosFaceJobRepository(session)
        job = jobs.enqueue(media)
        assert job is not None
        session.commit()

        claimed = jobs.claim_next()
        assert claimed is not None
        token = claimed.claim_token
        assert token is not None
        session.commit()

        analysis = FaceAnalysisResult(
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            detections=(
                FaceDetectionResult(
                    x=0.1,
                    y=0.2,
                    width=0.3,
                    height=0.4,
                    person_id="pessoa-inexistente",
                    confidence=0.95,
                ),
            ),
        )

        created = persist_face_analysis(
            session,
            job.id,
            token,
            analysis,
        )
        session.commit()

        faces = session.scalars(
            select(FotosFaceModel).where(FotosFaceModel.media_id == media.id)
        ).all()

        assert created == 1
        assert len(faces) == 1
        assert faces[0].status == "unknown"
        assert faces[0].person_id is None
        assert faces[0].confidence is None
        assert faces[0].origin == "detected"


def test_face_analysis_rejects_inactive_person(
    favorite_media_context,
) -> None:
    """Uma pessoa inativa não pode ser sugerida pela IA."""

    from uuid import uuid4

    from deja_platform_api.fotos.people.models import FotosPersonModel

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"

        person = FotosPersonModel(
            id=str(uuid4()),
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            name="Pessoa Inativa Teste",
            active=False,
        )

        session.add(person)
        session.commit()

        jobs = FotosFaceJobRepository(session)
        job = jobs.enqueue(media)
        assert job is not None
        session.commit()

        claimed = jobs.claim_next()
        assert claimed is not None

        token = claimed.claim_token
        assert token is not None
        session.commit()

        analysis = FaceAnalysisResult(
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            detections=(
                FaceDetectionResult(
                    x=0.1,
                    y=0.2,
                    width=0.3,
                    height=0.4,
                    person_id=person.id,
                    confidence=0.95,
                ),
            ),
        )

        created = persist_face_analysis(session, job.id, token, analysis)
        session.commit()

        faces = session.scalars(
            select(FotosFaceModel).where(FotosFaceModel.media_id == media.id)
        ).all()

        assert created == 1
        assert len(faces) == 1
        assert faces[0].status == "unknown"
        assert faces[0].person_id is None
        assert faces[0].confidence is None
        assert faces[0].origin == "detected"


def test_face_analysis_accepts_valid_person(
    favorite_media_context,
) -> None:
    """Uma pessoa ativa do mesmo ambiente pode ser sugerida pela IA."""

    from uuid import uuid4

    from deja_platform_api.fotos.people.models import FotosPersonModel

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"

        person = FotosPersonModel(
            id=str(uuid4()),
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            name="Pessoa Valida Teste",
            active=True,
        )

        session.add(person)
        session.commit()

        jobs = FotosFaceJobRepository(session)
        job = jobs.enqueue(media)
        assert job is not None
        session.commit()

        claimed = jobs.claim_next()
        assert claimed is not None
        token = claimed.claim_token
        assert token is not None
        session.commit()

        analysis = FaceAnalysisResult(
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            detections=(
                FaceDetectionResult(
                    x=0.1,
                    y=0.2,
                    width=0.3,
                    height=0.4,
                    person_id=person.id,
                    confidence=0.95,
                ),
            ),
        )

        created = persist_face_analysis(session, job.id, token, analysis)
        session.commit()

        faces = session.scalars(
            select(FotosFaceModel).where(FotosFaceModel.media_id == media.id)
        ).all()

        assert created == 1
        assert len(faces) == 1
        assert faces[0].origin == "detected"
        assert faces[0].status == "suggested"
        assert faces[0].person_id == person.id
        assert faces[0].confidence == pytest.approx(0.95)


def test_face_analysis_rejects_person_from_another_environment(
    favorite_media_context,
) -> None:
    """Uma pessoa de outro ambiente não pode ser sugerida pela IA."""

    from uuid import uuid4

    from deja_platform_api.fotos.people.models import FotosPersonModel

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"

        person = FotosPersonModel(
            id=str(uuid4()),
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=str(uuid4()),
            name="Pessoa Outro Ambiente Teste",
            active=True,
        )

        session.add(person)
        session.commit()

        jobs = FotosFaceJobRepository(session)
        job = jobs.enqueue(media)
        assert job is not None
        session.commit()

        claimed = jobs.claim_next()
        assert claimed is not None
        token = claimed.claim_token
        assert token is not None
        session.commit()

        analysis = FaceAnalysisResult(
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            detections=(
                FaceDetectionResult(
                    x=0.1,
                    y=0.2,
                    width=0.3,
                    height=0.4,
                    person_id=person.id,
                    confidence=0.95,
                ),
            ),
        )

        created = persist_face_analysis(session, job.id, token, analysis)
        session.commit()

        faces = session.scalars(
            select(FotosFaceModel).where(FotosFaceModel.media_id == media.id)
        ).all()

        assert created == 1
        assert len(faces) == 1
        assert faces[0].status == "unknown"
        assert faces[0].person_id is None
        assert faces[0].confidence is None


def test_face_analysis_rollback_preserves_job_and_faces(
    favorite_media_context,
) -> None:
    """Reverter a transação desfaz rostos e conclusão da tarefa."""

    from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"
        session.commit()

        jobs = FotosFaceJobRepository(session)
        job = jobs.enqueue(media)
        assert job is not None
        session.commit()

        claimed = jobs.claim_next()
        assert claimed is not None
        token = claimed.claim_token
        assert token is not None
        session.commit()

        analysis = FaceAnalysisResult(
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            detections=(
                FaceDetectionResult(
                    x=0.1,
                    y=0.2,
                    width=0.3,
                    height=0.4,
                ),
            ),
        )

        created = persist_face_analysis(session, job.id, token, analysis)

        assert created == 1
        session.rollback()

        remaining_faces = session.scalar(
            select(func.count(FotosFaceModel.id)).where(FotosFaceModel.media_id == media.id)
        )

        current_job = session.get(FotosFaceJobModel, job.id)

        assert remaining_faces == 0
        assert current_job is not None
        assert current_job.status == "processing"
        assert current_job.claim_token == token
        assert current_job.completed_at is None
