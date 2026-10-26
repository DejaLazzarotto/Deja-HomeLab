"""Testes da fila persistente de reconhecimento facial do VIVARO."""

from unittest.mock import MagicMock

from sqlalchemy import func, select

from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
from deja_platform_api.fotos.curation.job_repository import FotosFaceJobRepository
from deja_platform_api.fotos.media.models import FotosMediaModel

pytest_plugins = ("tests.fotos.media.test_favorite_repository",)


def test_video_is_not_added_to_face_queue() -> None:
    session = MagicMock()
    repository = FotosFaceJobRepository(session)

    media = FotosMediaModel(
        media_type="video",
        processing_status="ready",
        deleted_at=None,
    )

    assert repository.enqueue(media) is None
    session.execute.assert_not_called()


def test_unprocessed_image_is_not_added_to_face_queue() -> None:
    session = MagicMock()
    repository = FotosFaceJobRepository(session)

    media = FotosMediaModel(
        media_type="image",
        processing_status="received",
        deleted_at=None,
    )

    assert repository.enqueue(media) is None
    session.execute.assert_not_called()


def test_deleted_image_is_not_added_to_face_queue() -> None:
    session = MagicMock()
    repository = FotosFaceJobRepository(session)

    media = FotosMediaModel(
        media_type="image",
        processing_status="ready",
    )
    media.deleted_at = __import__("datetime").datetime.now()

    assert repository.enqueue(media) is None
    session.execute.assert_not_called()


def test_face_job_enqueue_is_idempotent(
    favorite_media_context,
) -> None:
    """Uma fotografia deve possuir somente um trabalho facial."""

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)

        assert media is not None

        # Simula a conclusão do processamento normal da imagem.
        media.processing_status = "ready"
        session.commit()

        repository = FotosFaceJobRepository(session)

        first = repository.enqueue(media)
        assert first is not None
        session.commit()

        original_id = first.id

        second = repository.enqueue(media)
        assert second is not None
        session.commit()

        assert second.id == original_id
        assert second.status == "pending"

        total = session.scalar(
            select(func.count(FotosFaceJobModel.id)).where(FotosFaceJobModel.media_id == media_id)
        )

        assert total == 1


def test_face_job_claim_next_reserves_only_once(
    favorite_media_context,
) -> None:
    """Uma fotografia pendente não pode ser reservada duas vezes."""

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None

        media.processing_status = "ready"
        session.commit()

        repository = FotosFaceJobRepository(session)

        job = repository.enqueue(media)
        assert job is not None
        session.commit()

        claimed = repository.claim_next()
        assert claimed is not None
        assert claimed.id == job.id
        assert claimed.status == "processing"
        assert claimed.attempts == 1
        assert claimed.claim_token is not None

        session.commit()

        second_claim = repository.claim_next()
        assert second_claim is None


def test_face_job_completion_requires_valid_token(
    favorite_media_context,
) -> None:
    """Somente a reserva válida pode concluir o trabalho."""

    import pytest

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"
        session.commit()

        repository = FotosFaceJobRepository(session)
        job = repository.enqueue(media)
        assert job is not None
        session.commit()

        claimed = repository.claim_next()
        assert claimed is not None
        token = claimed.claim_token
        assert token is not None
        session.commit()

        with pytest.raises(RuntimeError, match="Reserva facial inválida"):
            repository.complete(claimed, "token-invalido")

        session.rollback()
        session.expire_all()

        current = session.get(FotosFaceJobModel, job.id)
        assert current is not None
        assert current.status == "processing"

        repository.complete(current, token)
        session.commit()
        session.expire_all()

        completed = session.get(FotosFaceJobModel, job.id)
        assert completed is not None
        assert completed.status == "completed"
        assert completed.claim_token is None
        assert completed.completed_at is not None


def test_face_job_failure_schedules_retry(
    favorite_media_context,
) -> None:
    """Uma falha deve liberar a reserva e agendar nova tentativa."""

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None

        media.processing_status = "ready"
        session.commit()

        repository = FotosFaceJobRepository(session)

        job = repository.enqueue(media)
        assert job is not None
        session.commit()

        claimed = repository.claim_next()
        assert claimed is not None

        token = claimed.claim_token
        assert token is not None
        session.commit()

        repository.fail(
            claimed,
            token,
            "Falha temporaria no reconhecimento facial",
            retry_delay_seconds=60,
        )
        session.commit()
        session.expire_all()

        current = session.get(FotosFaceJobModel, job.id)

        assert current is not None
        assert current.status == "pending"
        assert current.attempts == 1
        assert current.claim_token is None
        assert current.next_attempt_at is not None
        assert "Falha temporaria" in current.last_error

        assert repository.claim_next() is None


def test_face_job_stops_after_max_attempts(
    favorite_media_context,
) -> None:
    """O trabalho deve parar após esgotar as tentativas."""

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None

        media.processing_status = "ready"
        session.commit()

        repository = FotosFaceJobRepository(session)

        job = repository.enqueue(media)
        assert job is not None
        session.commit()

        # Simula um trabalho que já falhou duas vezes.
        job.attempts = 2
        session.commit()

        claimed = repository.claim_next()
        assert claimed is not None
        assert claimed.attempts == 3

        token = claimed.claim_token
        assert token is not None
        session.commit()

        repository.fail(
            claimed,
            token,
            "Terceira falha no reconhecimento facial",
        )
        session.commit()
        session.expire_all()

        current = session.get(FotosFaceJobModel, job.id)

        assert current is not None
        assert current.status == "failed"
        assert current.attempts == 3
        assert current.claim_token is None
        assert current.next_attempt_at is None
        assert "Terceira falha" in current.last_error

        assert repository.claim_next() is None


def test_face_job_recovers_interrupted_processing(
    favorite_media_context,
) -> None:
    """Recupera um trabalho expirado e invalida sua reserva antiga."""

    from datetime import timedelta

    from deja_platform_api.fotos.curation.job_repository import utc_now

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None

        media.processing_status = "ready"
        session.commit()

        repository = FotosFaceJobRepository(session)

        job = repository.enqueue(media)
        assert job is not None
        session.commit()

        claimed = repository.claim_next()
        assert claimed is not None

        old_token = claimed.claim_token
        assert old_token is not None

        claimed.started_at = utc_now() - timedelta(minutes=40)
        session.commit()

        recovered = repository.recover_stale(timeout_minutes=30)
        assert recovered == 1
        session.commit()
        session.expire_all()

        current = session.get(FotosFaceJobModel, job.id)
        assert current is not None
        assert current.status == "pending"
        assert current.claim_token is None
        assert current.started_at is None
        assert current.attempts == 1

        new_claim = repository.claim_next()
        assert new_claim is not None
        assert new_claim.claim_token is not None
        assert new_claim.claim_token != old_token


def test_face_job_rejects_expired_claim_token(
    favorite_media_context,
) -> None:
    """Uma reserva antiga não pode concluir um trabalho recuperado."""

    from datetime import timedelta

    import pytest

    from deja_platform_api.fotos.curation.job_repository import utc_now

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None
        media.processing_status = "ready"
        session.commit()

        repository = FotosFaceJobRepository(session)

        job = repository.enqueue(media)
        assert job is not None
        session.commit()

        first_claim = repository.claim_next()
        assert first_claim is not None

        old_token = first_claim.claim_token
        assert old_token is not None

        first_claim.started_at = utc_now() - timedelta(minutes=40)
        session.commit()

        assert repository.recover_stale(timeout_minutes=30) == 1
        session.commit()

        new_claim = repository.claim_next()
        assert new_claim is not None
        new_token = new_claim.claim_token
        assert new_token is not None
        assert new_token != old_token
        session.commit()

        with pytest.raises(RuntimeError, match="Reserva facial inválida"):
            repository.complete(new_claim, old_token)

        session.rollback()
        session.expire_all()

        current = session.get(FotosFaceJobModel, job.id)
        assert current is not None
        assert current.status == "processing"
        assert current.claim_token == new_token


def test_face_job_lock_requires_valid_claim(
    favorite_media_context,
) -> None:
    """Somente a reserva atual permite bloquear o trabalho."""

    import pytest

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        media = session.get(FotosMediaModel, media_id)
        assert media is not None

        media.processing_status = "ready"
        session.commit()

        repository = FotosFaceJobRepository(session)

        job = repository.enqueue(media)
        assert job is not None
        session.commit()

        claimed = repository.claim_next()
        assert claimed is not None

        token = claimed.claim_token
        assert token is not None
        session.commit()

        locked = repository.lock_valid_claim(job.id, token)

        assert locked.id == job.id
        assert locked.status == "processing"
        assert locked.claim_token == token

        with pytest.raises(RuntimeError, match="Reserva facial inválida"):
            repository.lock_valid_claim(job.id, "token-invalido")

        session.rollback()


def test_media_and_face_job_are_created_atomically(
    favorite_media_context,
) -> None:
    """Uma fotografia nova e seu trabalho facial são gravados juntos."""
    from uuid import uuid4

    from sqlalchemy import select

    from deja_platform_api.fotos.curation.job_models import FotosFaceJobModel
    from deja_platform_api.fotos.media.repository import FotosMediaRepository

    media_id = favorite_media_context["media_id"]
    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        original = session.get(FotosMediaModel, media_id)
        assert original is not None

        new_media_id = str(uuid4())

        values = {
            column.name: getattr(original, column.name)
            for column in FotosMediaModel.__table__.columns
            if column.name not in {"id", "created_at", "updated_at"}
        }

        values["id"] = new_media_id
        values["source_checksum_sha256"] = uuid4().hex * 2
        values["checksum_sha256"] = uuid4().hex * 2
        values["original_storage_key"] = f"homologacao/{new_media_id}.jpg"
        values["processing_status"] = "received"

        new_media = FotosMediaModel(**values)

        repository = FotosMediaRepository(session)
        saved = repository.add_with_face_job(new_media)

        assert saved.id == new_media_id

        jobs = session.scalars(
            select(FotosFaceJobModel).where(FotosFaceJobModel.media_id == new_media_id)
        ).all()

        assert len(jobs) == 1
        assert jobs[0].status == "pending"
        assert jobs[0].attempts == 0
        assert jobs[0].organization_id == saved.organization_id
        assert jobs[0].tenant_id == saved.tenant_id
        assert jobs[0].environment_id == saved.environment_id


def test_media_creation_rolls_back_when_face_job_fails(
    favorite_media_context,
) -> None:
    """Falha no trabalho facial desfaz também o cadastro da fotografia."""
    from uuid import uuid4

    import pytest
    from sqlalchemy import event

    from deja_platform_api.fotos.media.repository import FotosMediaRepository

    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        original = session.get(
            FotosMediaModel,
            favorite_media_context["media_id"],
        )
        assert original is not None

        new_id = str(uuid4())
        values = {
            column.name: getattr(original, column.name)
            for column in FotosMediaModel.__table__.columns
            if column.name not in {"id", "created_at", "updated_at"}
        }
        values.update(
            id=new_id,
            source_checksum_sha256=uuid4().hex * 2,
            checksum_sha256=uuid4().hex * 2,
            original_storage_key=f"homologacao/{new_id}.jpg",
            processing_status="received",
        )

        new_media = FotosMediaModel(**values)

        def reject_face_job(mapper, connection, target):
            if target.media_id == new_id:
                raise RuntimeError("Falha simulada na criação do trabalho facial")

        event.listen(
            FotosFaceJobModel,
            "before_insert",
            reject_face_job,
        )
        try:
            with pytest.raises(
                RuntimeError,
                match="Falha simulada na criação",
            ):
                FotosMediaRepository(session).add_with_face_job(new_media)
        finally:
            event.remove(
                FotosFaceJobModel,
                "before_insert",
                reject_face_job,
            )

        session.expire_all()

        assert session.get(FotosMediaModel, new_id) is None

        remaining_job = session.scalar(
            select(FotosFaceJobModel).where(FotosFaceJobModel.media_id == new_id)
        )
        assert remaining_job is None


def test_add_with_face_job_rejects_video(
    favorite_media_context,
) -> None:
    """Vídeos não podem receber trabalhos de reconhecimento facial."""
    from uuid import uuid4

    import pytest

    from deja_platform_api.fotos.media.repository import FotosMediaRepository

    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        original = session.get(
            FotosMediaModel,
            favorite_media_context["media_id"],
        )
        assert original is not None

        video_id = str(uuid4())
        video = FotosMediaModel(
            id=video_id,
            organization_id=original.organization_id,
            tenant_id=original.tenant_id,
            environment_id=original.environment_id,
            media_type="video",
            processing_status="received",
        )

        with pytest.raises(
            ValueError,
            match="exige uma fotografia",
        ):
            FotosMediaRepository(session).add_with_face_job(video)

        assert session.get(FotosMediaModel, video_id) is None
        assert (
            session.scalar(select(FotosFaceJobModel).where(FotosFaceJobModel.media_id == video_id))
            is None
        )


def test_face_job_waits_until_photo_is_ready(
    favorite_media_context,
) -> None:
    """A fila facial aguarda a conclusão dos derivados da fotografia."""
    from uuid import uuid4

    from deja_platform_api.fotos.media.repository import FotosMediaRepository

    session_factory = favorite_media_context["session_factory"]

    with session_factory() as session:
        original = session.get(
            FotosMediaModel,
            favorite_media_context["media_id"],
        )
        assert original is not None

        new_id = str(uuid4())
        values = {
            column.name: getattr(original, column.name)
            for column in FotosMediaModel.__table__.columns
            if column.name not in {"id", "created_at", "updated_at"}
        }
        values.update(
            id=new_id,
            source_checksum_sha256=uuid4().hex * 2,
            checksum_sha256=uuid4().hex * 2,
            original_storage_key=f"homologacao/{new_id}.jpg",
            processing_status="received",
        )

        media = FotosMediaModel(**values)
        FotosMediaRepository(session).add_with_face_job(media)

        repository = FotosFaceJobRepository(session)

        # Isola o trabalho desta fotografia dos demais trabalhos da fixture.
        from sqlalchemy import update

        session.execute(
            update(FotosFaceJobModel)
            .where(FotosFaceJobModel.media_id != new_id)
            .values(status="completed")
        )
        session.commit()

        # A fotografia ainda não está pronta.
        # Outros trabalhos elegíveis podem existir nesta fila compartilhada.
        first_claim = repository.claim_next()
        assert first_claim is None or first_claim.media_id != new_id
        session.rollback()

        job = session.scalar(select(FotosFaceJobModel).where(FotosFaceJobModel.media_id == new_id))
        assert job is not None
        assert job.status == "pending"

        # Simula a conclusão da geração dos derivados.
        media.processing_status = "ready"
        session.commit()

        claimed = repository.claim_next()

        assert claimed is not None
        assert claimed.id == job.id
        assert claimed.status == "processing"
        assert claimed.attempts == 1
        assert claimed.claim_token is not None

        session.commit()
