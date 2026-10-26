"""Testes do worker de reconhecimento facial automático."""

from pathlib import Path
from unittest.mock import Mock, patch

from deja_platform_api.fotos.curation.worker import process_next_face_job

pytest_plugins = ("tests.fotos.media.test_favorite_repository",)


def test_worker_does_nothing_when_queue_is_empty(
    favorite_media_context,
) -> None:
    """Uma fila vazia não deve iniciar análise facial."""

    session_factory = favorite_media_context["session_factory"]
    resolve_image_path = Mock()

    with patch("deja_platform_api.fotos.curation.worker.FotosFaceJobRepository") as jobs:
        jobs.return_value.claim_next.return_value = None

        processed = process_next_face_job(
            session_factory=session_factory,
            resolve_image_path=resolve_image_path,
            uploads_dir=Path("uploads"),
            models_dir=Path("models"),
        )

    assert processed is False
    resolve_image_path.assert_not_called()


def test_worker_processes_one_photo_successfully(
    favorite_media_context,
) -> None:
    """Processa uma fotografia e conclui o trabalho facial."""

    from unittest.mock import patch

    from sqlalchemy import func, select

    from deja_platform_api.fotos.curation.analysis_models import (
        FaceAnalysisResult,
        FaceDetectionResult,
    )
    from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
    from deja_platform_api.fotos.curation.job_repository import FotosFaceJobRepository
    from deja_platform_api.fotos.curation.models import FotosFaceModel
    from deja_platform_api.fotos.media.models import FotosMediaModel

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
        job_id = job.id
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

    with patch(
        "deja_platform_api.fotos.curation.worker.analyze_faces",
        return_value=analysis,
    ) as analyzer:
        processed = process_next_face_job(
            session_factory=session_factory,
            resolve_image_path=lambda media: Path("foto-teste.jpg"),
            uploads_dir=Path("uploads"),
            models_dir=Path("models"),
        )

    assert processed is True
    analyzer.assert_called_once()

    with session_factory() as session:
        current_job = session.get(FotosFaceJobModel, job_id)

        assert current_job is not None
        assert current_job.status == "completed"
        assert current_job.claim_token is None
        assert current_job.completed_at is not None

        total_faces = session.scalar(
            select(func.count(FotosFaceModel.id)).where(FotosFaceModel.media_id == media_id)
        )

        assert total_faces == 1


def test_worker_schedules_retry_after_analysis_failure(
    favorite_media_context,
) -> None:
    """Falha na análise deve reagendar o trabalho sem criar rostos."""

    from unittest.mock import patch

    from sqlalchemy import func, select

    from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
    from deja_platform_api.fotos.curation.job_repository import FotosFaceJobRepository
    from deja_platform_api.fotos.curation.models import FotosFaceModel
    from deja_platform_api.fotos.media.models import FotosMediaModel

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
        job_id = job.id
        session.commit()

    with patch(
        "deja_platform_api.fotos.curation.worker.analyze_faces",
        side_effect=RuntimeError("Falha simulada no YuNet"),
    ):
        processed = process_next_face_job(
            session_factory=session_factory,
            resolve_image_path=lambda media: Path("foto-teste.jpg"),
            uploads_dir=Path("uploads"),
            models_dir=Path("models"),
        )

    assert processed is True

    with session_factory() as session:
        job = session.get(FotosFaceJobModel, job_id)
        media = session.get(FotosMediaModel, media_id)

        assert job is not None
        assert job.status == "pending"
        assert job.attempts == 1
        assert job.claim_token is None
        assert job.next_attempt_at is not None
        assert "Falha simulada no YuNet" in job.last_error

        assert media is not None
        assert media.processing_status == "ready"

        total_faces = session.scalar(
            select(func.count(FotosFaceModel.id)).where(FotosFaceModel.media_id == media_id)
        )

        assert total_faces == 0


def test_worker_cannot_persist_after_claim_is_recovered(
    favorite_media_context,
) -> None:
    """O worker não grava rostos quando perde sua reserva durante a análise."""

    from datetime import timedelta
    from unittest.mock import patch

    from sqlalchemy import func, select

    from deja_platform_api.fotos.curation.analysis_models import (
        FaceAnalysisResult,
        FaceDetectionResult,
    )
    from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
    from deja_platform_api.fotos.curation.job_repository import (
        FotosFaceJobRepository,
        utc_now,
    )
    from deja_platform_api.fotos.curation.models import FotosFaceModel
    from deja_platform_api.fotos.media.models import FotosMediaModel

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
        job_id = job.id
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

    def simulate_expired_claim(*args, **kwargs):
        with session_factory() as session:
            jobs = FotosFaceJobRepository(session)
            job = session.get(FotosFaceJobModel, job_id)
            assert job is not None

            job.started_at = utc_now() - timedelta(minutes=40)
            session.commit()

            assert jobs.recover_stale(timeout_minutes=30) == 1
            session.commit()

        return analysis

    with patch(
        "deja_platform_api.fotos.curation.worker.analyze_faces",
        side_effect=simulate_expired_claim,
    ):
        processed = process_next_face_job(
            session_factory=session_factory,
            resolve_image_path=lambda media: Path("foto-teste.jpg"),
            uploads_dir=Path("uploads"),
            models_dir=Path("models"),
        )

    assert processed is True

    with session_factory() as session:
        job = session.get(FotosFaceJobModel, job_id)
        assert job is not None
        assert job.status == "pending"
        assert job.claim_token is None

        total_faces = session.scalar(
            select(func.count(FotosFaceModel.id)).where(FotosFaceModel.media_id == media_id)
        )

        assert total_faces == 0
