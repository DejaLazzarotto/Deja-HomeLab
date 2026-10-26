"""Testes da integração entre processamento de mídia e fila facial."""

from unittest.mock import MagicMock, patch

from deja_platform_api.fotos.media.background_processing import (
    process_media_in_background,
)


def test_background_processing_enqueues_ready_photo() -> None:
    """Fotografia pronta deve entrar na fila de reconhecimento facial."""

    media = MagicMock()
    media.id = "foto-teste"
    media.media_type = "image"
    media.processing_status = "ready"
    media.deleted_at = None

    session = MagicMock()
    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = session

    with (
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosMediaRepository"
        ) as media_repository,
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosMediaDerivativeService"
        ) as derivative_service,
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosFaceJobRepository"
        ) as face_jobs,
    ):
        media_repository.return_value.find_by_id.return_value = media

        process_media_in_background(
            media.id,
            session_factory=session_factory,
            settings=MagicMock(),
        )

        derivative_service.return_value.process.assert_called_once_with(media)
        face_jobs.return_value.enqueue.assert_called_once_with(media)
        session.commit.assert_called_once()


def test_face_queue_failure_does_not_break_media_processing() -> None:
    """Falha na fila facial não pode invalidar fotografia já processada."""

    media = MagicMock()
    media.id = "foto-falha-fila"
    media.media_type = "image"
    media.processing_status = "ready"
    media.deleted_at = None

    session = MagicMock()
    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = session

    with (
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosMediaRepository"
        ) as media_repository,
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosMediaDerivativeService"
        ) as derivative_service,
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosFaceJobRepository"
        ) as face_jobs,
    ):
        media_repository.return_value.find_by_id.return_value = media
        face_jobs.return_value.enqueue.side_effect = RuntimeError("Falha simulada na fila facial")

        process_media_in_background(
            media.id,
            session_factory=session_factory,
            settings=MagicMock(),
        )

        derivative_service.return_value.process.assert_called_once_with(media)
        assert media.processing_status == "ready"
        session.rollback.assert_called_once()


def test_background_processing_does_not_enqueue_video() -> None:
    """Vídeos processados não devem entrar na fila facial."""

    media = MagicMock()
    media.id = "video-teste"
    media.media_type = "video"
    media.processing_status = "ready"
    media.deleted_at = None

    session = MagicMock()
    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = session

    with (
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosMediaRepository"
        ) as media_repository,
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosMediaDerivativeService"
        ) as derivative_service,
        patch(
            "deja_platform_api.fotos.media.background_processing.FotosFaceJobRepository"
        ) as face_jobs,
    ):
        media_repository.return_value.find_by_id.return_value = media

        process_media_in_background(
            media.id,
            session_factory=session_factory,
            settings=MagicMock(),
        )

        derivative_service.return_value.process.assert_called_once_with(media)
        face_jobs.assert_not_called()
