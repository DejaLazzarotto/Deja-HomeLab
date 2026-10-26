"""Testes do executor independente de reconhecimento facial."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from deja_platform_api.fotos.curation.worker_runner import resolve_preview_path


def test_resolve_preview_path_returns_existing_file(tmp_path: Path) -> None:
    """Localiza o preview cadastrado no banco."""

    preview = tmp_path / "fotos" / "preview.webp"
    preview.parent.mkdir(parents=True)
    preview.write_bytes(b"preview-teste")

    media = SimpleNamespace(id="foto-1")
    derivative = SimpleNamespace(storage_key="fotos/preview.webp")

    with (
        patch("deja_platform_api.fotos.curation.worker_runner.get_settings") as settings,
        patch("deja_platform_api.fotos.curation.worker_runner.SessionLocal") as session_factory,
        patch(
            "deja_platform_api.fotos.curation.worker_runner.FotosMediaDerivativeRepository"
        ) as repository,
    ):
        settings.return_value.uploads_dir = tmp_path
        session_factory.return_value.__enter__.return_value = MagicMock()
        repository.return_value.find_by_media_and_type.return_value = derivative

        result = resolve_preview_path(media)

    assert result == preview
    repository.return_value.find_by_media_and_type.assert_called_once_with("foto-1", "preview")


def test_resolve_preview_path_rejects_missing_derivative(tmp_path: Path) -> None:
    """Não permite analisar fotografia sem preview cadastrado."""

    media = SimpleNamespace(id="foto-sem-preview")

    with (
        patch("deja_platform_api.fotos.curation.worker_runner.get_settings") as settings,
        patch("deja_platform_api.fotos.curation.worker_runner.SessionLocal"),
        patch(
            "deja_platform_api.fotos.curation.worker_runner.FotosMediaDerivativeRepository"
        ) as repository,
    ):
        settings.return_value.uploads_dir = tmp_path
        repository.return_value.find_by_media_and_type.return_value = None

        with pytest.raises(FileNotFoundError, match="Preview não encontrado"):
            resolve_preview_path(media)


def test_resolve_preview_path_blocks_directory_traversal(tmp_path: Path) -> None:
    """Um storage_key não pode acessar arquivos fora de UPLOADS_DIR."""

    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()

    outside_file = tmp_path / "arquivo-externo.webp"
    outside_file.write_bytes(b"arquivo-privado")

    media = SimpleNamespace(id="foto-caminho-invalido")
    derivative = SimpleNamespace(storage_key="../arquivo-externo.webp")

    with (
        patch("deja_platform_api.fotos.curation.worker_runner.get_settings") as settings,
        patch("deja_platform_api.fotos.curation.worker_runner.SessionLocal"),
        patch(
            "deja_platform_api.fotos.curation.worker_runner.FotosMediaDerivativeRepository"
        ) as repository,
    ):
        settings.return_value.uploads_dir = uploads_dir
        repository.return_value.find_by_media_and_type.return_value = derivative

        with pytest.raises(
            ValueError,
            match="Caminho de preview fora do diretório autorizado",
        ):
            resolve_preview_path(media)


def test_worker_cycle_recovers_jobs_before_processing() -> None:
    """O executor recupera trabalhos interrompidos antes de consumir a fila."""

    from deja_platform_api.fotos.curation.worker_runner import run_worker_cycle

    settings = SimpleNamespace(
        uploads_dir=Path("uploads"),
        fotos_face_models_dir=Path("models"),
    )

    events = []

    session = MagicMock()
    session.commit.side_effect = lambda: events.append("commit")

    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = session

    with (
        patch(
            "deja_platform_api.fotos.curation.worker_runner.SessionLocal",
            session_factory,
        ),
        patch("deja_platform_api.fotos.curation.worker_runner.FotosFaceJobRepository") as jobs,
        patch("deja_platform_api.fotos.curation.worker_runner.process_next_face_job") as processor,
    ):
        jobs.return_value.recover_stale.side_effect = lambda: events.append("recover") or 1
        processor.side_effect = lambda **kwargs: events.append("process") or True

        processed = run_worker_cycle(settings)

    assert processed is True
    assert events == ["recover", "commit", "process"]

    jobs.return_value.recover_stale.assert_called_once_with()
    processor.assert_called_once_with(
        session_factory=session_factory,
        resolve_image_path=resolve_preview_path,
        uploads_dir=settings.uploads_dir,
        models_dir=settings.fotos_face_models_dir,
    )


def test_worker_cycle_stops_when_recovery_fails() -> None:
    """Falha na recuperação impede iniciar outro processamento facial."""

    from deja_platform_api.fotos.curation.worker_runner import run_worker_cycle

    settings = SimpleNamespace(
        uploads_dir=Path("uploads"),
        fotos_face_models_dir=Path("models"),
    )

    session = MagicMock()
    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = session

    with (
        patch(
            "deja_platform_api.fotos.curation.worker_runner.SessionLocal",
            session_factory,
        ),
        patch("deja_platform_api.fotos.curation.worker_runner.FotosFaceJobRepository") as jobs,
        patch("deja_platform_api.fotos.curation.worker_runner.process_next_face_job") as processor,
    ):
        jobs.return_value.recover_stale.side_effect = RuntimeError(
            "Falha simulada na recuperação da fila"
        )

        with pytest.raises(
            RuntimeError,
            match="Falha simulada na recuperação da fila",
        ):
            run_worker_cycle(settings)

        processor.assert_not_called()
        session.commit.assert_not_called()
