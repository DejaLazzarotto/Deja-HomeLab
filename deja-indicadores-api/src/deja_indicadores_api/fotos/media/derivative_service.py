from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.fotos.media.derivative_models import (
    FotosMediaDerivativeModel,
)
from deja_indicadores_api.fotos.media.derivative_repository import (
    FotosMediaDerivativeRepository,
)
from deja_indicadores_api.fotos.media.exceptions import (
    FotosMediaAlreadyProcessingError,
)
from deja_indicadores_api.fotos.media.image_derivatives import (
    FotosImageDerivative,
    generate_image_derivative,
)
from deja_indicadores_api.fotos.media.models import (
    FotosMediaModel,
)
from deja_indicadores_api.fotos.media.repository import (
    FotosMediaRepository,
)
from deja_indicadores_api.fotos.media.video_derivatives import (
    FotosVideoDerivative,
    generate_video_poster,
    generate_video_preview,
)
from deja_indicadores_api.fotos.media.video_inspection import (
    FotosVideoInspectionError,
    inspect_video,
)


class FotosMediaDerivativeService:
    """Processamento dos arquivos derivados de mídias."""

    def __init__(
        self,
        media_repository: FotosMediaRepository,
        derivative_repository: FotosMediaDerivativeRepository,
        settings: Settings,
    ) -> None:
        self._media_repository = media_repository
        self._derivative_repository = derivative_repository
        self._settings = settings

    def process(
        self,
        media: FotosMediaModel,
    ) -> list[FotosMediaDerivativeModel]:
        """Processa os derivados conforme o tipo da mídia."""

        if media.media_type == "image":
            return self.process_image(media)

        if media.media_type == "video":
            return self.process_video(media)

        raise ValueError("Tipo de mídia não suportado para processamento.")

    def _claim_processing(
        self,
        media: FotosMediaModel,
    ) -> None:
        """Assume uma tentativa ou rejeita processamento concorrente."""

        started_at = datetime.now(UTC).replace(tzinfo=None)
        stale_before = started_at - timedelta(
            minutes=self._settings.fotos_media_processing_timeout_minutes,
        )

        claimed = self._media_repository.try_start_processing(
            media,
            stale_before=stale_before,
            started_at=started_at,
        )

        if not claimed:
            raise FotosMediaAlreadyProcessingError(media.id)

    def process_image(
        self,
        media: FotosMediaModel,
    ) -> list[FotosMediaDerivativeModel]:
        """Gera thumbnail e preview de uma imagem."""

        if media.media_type != "image":
            raise ValueError("A mídia informada não é uma imagem.")

        original_path = self._resolve_original_path(media)

        self._claim_processing(media)

        derivatives: list[FotosMediaDerivativeModel] = []

        newly_created: list[FotosMediaDerivativeModel] = []

        try:
            for derivative_type in (
                "thumbnail",
                "preview",
            ):
                (
                    derivative,
                    was_created,
                ) = self._generate_image_derivative(
                    media,
                    original_path=original_path,
                    derivative_type=derivative_type,
                )

                derivatives.append(derivative)

                if was_created:
                    newly_created.append(derivative)

        except Exception as exc:
            self._cleanup_new_derivatives(newly_created)

            media.processing_status = "failed"
            media.processing_error = str(exc)

            self._media_repository.update(media)

            raise

        media.processing_status = "ready"
        media.processing_error = None

        self._media_repository.update(media)

        return derivatives

    def process_video(
        self,
        media: FotosMediaModel,
    ) -> list[FotosMediaDerivativeModel]:
        """Gera poster e preview de um vídeo."""

        if media.media_type != "video":
            raise ValueError("A mídia informada não é um vídeo.")

        original_path = self._resolve_original_path(media)

        duration_seconds = media.duration_seconds
        width = media.width
        height = media.height

        if duration_seconds is None or duration_seconds <= 0:
            raise ValueError("A mídia não possui duração de vídeo válida.")

        if width is None or height is None or width <= 0 or height <= 0:
            raise ValueError("A mídia não possui dimensões de vídeo válidas.")

        self._claim_processing(media)

        derivatives: list[FotosMediaDerivativeModel] = []

        newly_created: list[FotosMediaDerivativeModel] = []

        try:
            (
                poster,
                poster_created,
            ) = self._generate_video_poster_derivative(
                media,
                original_path=original_path,
                duration_seconds=duration_seconds,
            )

            derivatives.append(poster)

            if poster_created:
                newly_created.append(poster)

            (
                preview,
                preview_created,
            ) = self._generate_video_preview_derivative(
                media,
                original_path=original_path,
                width=width,
                height=height,
            )

            derivatives.append(preview)

            if preview_created:
                newly_created.append(preview)

        except Exception as exc:
            self._cleanup_new_derivatives(newly_created)

            media.processing_status = "failed"
            media.processing_error = str(exc)

            self._media_repository.update(media)

            raise

        media.processing_status = "ready"
        media.processing_error = None

        self._media_repository.update(media)

        return derivatives

    def list_derivatives(
        self,
        media_id: str,
    ) -> list[FotosMediaDerivativeModel]:
        """Lista os derivados persistidos de uma mídia."""

        return self._derivative_repository.list_by_media_id(media_id)

    def get_derivative_file(
        self,
        media_id: str,
        derivative_type: str,
    ) -> tuple[
        Path,
        FotosMediaDerivativeModel,
    ]:
        """Retorna o arquivo físico de um derivado existente."""

        derivative = self._derivative_repository.find_by_media_and_type(
            media_id,
            derivative_type,
        )

        if derivative is None:
            raise FileNotFoundError("O derivado solicitado não foi encontrado.")

        file_path = self._settings.uploads_dir / Path(derivative.storage_key)

        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError("O arquivo físico do derivado não foi encontrado.")

        return file_path, derivative

    def _resolve_original_path(
        self,
        media: FotosMediaModel,
    ) -> Path:
        """Resolve e valida o caminho físico do original."""

        original_path = self._settings.uploads_dir / Path(media.original_storage_key)

        if not original_path.exists() or not original_path.is_file():
            raise FileNotFoundError("O arquivo original da mídia não foi encontrado.")

        return original_path

    def _is_derivative_file_valid(
        self,
        derivative: FotosMediaDerivativeModel,
    ) -> bool:
        """Valida o arquivo físico e os metadados de um derivado."""

        file_path = self._settings.uploads_dir / Path(
            derivative.storage_key
        )

        try:
            if not file_path.is_file():
                return False

            file_size = file_path.stat().st_size

            if file_size <= 0 or file_size != derivative.file_size:
                return False

            if derivative.content_type == "image/webp":
                with Image.open(file_path) as image:
                    image_format = image.format
                    image.load()
                    width, height = image.size

                return (
                    image_format == "WEBP"
                    and width == derivative.width
                    and height == derivative.height
                )

            if derivative.content_type == "video/mp4":
                inspection = inspect_video(
                    file_path,
                    ffprobe_executable=self._settings.ffprobe_executable,
                )

                return (
                    inspection.width == derivative.width
                    and inspection.height == derivative.height
                )

        except (
            FotosVideoInspectionError,
            OSError,
            UnidentifiedImageError,
            ValueError,
        ):
            return False

        return False

    def _update_existing_derivative(
        self,
        derivative: FotosMediaDerivativeModel,
        generated: FotosImageDerivative | FotosVideoDerivative,
        *,
        destination_path: Path,
    ) -> tuple[
        FotosMediaDerivativeModel,
        bool,
    ]:
        """Atualiza um registro depois de regenerar seu arquivo."""

        derivative.content_type = generated.content_type
        derivative.file_extension = generated.file_extension
        derivative.file_size = generated.file_size
        derivative.width = generated.width
        derivative.height = generated.height

        try:
            persisted = self._derivative_repository.update(
                derivative
            )
        except Exception:
            destination_path.unlink(
                missing_ok=True,
            )

            raise

        return persisted, False

    def _generate_image_derivative(
        self,
        media: FotosMediaModel,
        *,
        original_path: Path,
        derivative_type: str,
    ) -> tuple[
        FotosMediaDerivativeModel,
        bool,
    ]:
        """Gera e persiste um derivado individual de imagem."""

        existing = self._derivative_repository.find_by_media_and_type(
            media.id,
            derivative_type,
        )

        if (
            existing is not None
            and self._is_derivative_file_valid(existing)
        ):
            return existing, False

        if existing is not None:
            storage_key = Path(existing.storage_key)
        else:
            storage_key = self._build_derivative_storage_key(
                media,
                derivative_type,
                ".webp",
            )

        destination_path = self._settings.uploads_dir / storage_key

        generated = generate_image_derivative(
            original_path,
            destination_path,
            derivative_type=derivative_type,
        )

        if existing is not None:
            return self._update_existing_derivative(
                existing,
                generated,
                destination_path=destination_path,
            )

        derivative = FotosMediaDerivativeModel(
            id=str(uuid4()),
            media_id=media.id,
            derivative_type=derivative_type,
            storage_key=storage_key.as_posix(),
            content_type=generated.content_type,
            file_extension=generated.file_extension,
            file_size=generated.file_size,
            width=generated.width,
            height=generated.height,
        )

        return self._persist_derivative(
            derivative,
            destination_path=destination_path,
        )

    def _generate_video_poster_derivative(
        self,
        media: FotosMediaModel,
        *,
        original_path: Path,
        duration_seconds: float,
    ) -> tuple[
        FotosMediaDerivativeModel,
        bool,
    ]:
        """Gera e persiste o poster de um vídeo."""

        derivative_type = "poster"

        existing = self._derivative_repository.find_by_media_and_type(
            media.id,
            derivative_type,
        )

        if (
            existing is not None
            and self._is_derivative_file_valid(existing)
        ):
            return existing, False

        if existing is not None:
            storage_key = Path(existing.storage_key)
        else:
            storage_key = self._build_derivative_storage_key(
                media,
                derivative_type,
                ".webp",
            )

        destination_path = self._settings.uploads_dir / storage_key

        generated = generate_video_poster(
            original_path,
            destination_path,
            ffmpeg_executable=self._settings.ffmpeg_executable,
            duration_seconds=duration_seconds,
        )

        if existing is not None:
            return self._update_existing_derivative(
                existing,
                generated,
                destination_path=destination_path,
            )

        derivative = FotosMediaDerivativeModel(
            id=str(uuid4()),
            media_id=media.id,
            derivative_type=derivative_type,
            storage_key=storage_key.as_posix(),
            content_type=generated.content_type,
            file_extension=generated.file_extension,
            file_size=generated.file_size,
            width=generated.width,
            height=generated.height,
        )

        return self._persist_derivative(
            derivative,
            destination_path=destination_path,
        )

    def _generate_video_preview_derivative(
        self,
        media: FotosMediaModel,
        *,
        original_path: Path,
        width: int,
        height: int,
    ) -> tuple[
        FotosMediaDerivativeModel,
        bool,
    ]:
        """Gera e persiste o preview MP4 de um vídeo."""

        derivative_type = "preview"

        existing = self._derivative_repository.find_by_media_and_type(
            media.id,
            derivative_type,
        )

        if (
            existing is not None
            and self._is_derivative_file_valid(existing)
        ):
            return existing, False

        if existing is not None:
            storage_key = Path(existing.storage_key)
        else:
            storage_key = self._build_derivative_storage_key(
                media,
                derivative_type,
                ".mp4",
            )

        destination_path = self._settings.uploads_dir / storage_key

        generated = generate_video_preview(
            original_path,
            destination_path,
            ffmpeg_executable=self._settings.ffmpeg_executable,
            width=width,
            height=height,
        )

        if existing is not None:
            return self._update_existing_derivative(
                existing,
                generated,
                destination_path=destination_path,
            )

        derivative = FotosMediaDerivativeModel(
            id=str(uuid4()),
            media_id=media.id,
            derivative_type=derivative_type,
            storage_key=storage_key.as_posix(),
            content_type=generated.content_type,
            file_extension=generated.file_extension,
            file_size=generated.file_size,
            width=generated.width,
            height=generated.height,
        )

        return self._persist_derivative(
            derivative,
            destination_path=destination_path,
        )

    def _build_derivative_storage_key(
        self,
        media: FotosMediaModel,
        derivative_type: str,
        file_extension: str,
    ) -> Path:
        """Monta a chave de armazenamento de um derivado."""

        return (
            Path("fotos")
            / media.organization_id
            / media.tenant_id
            / media.environment_id
            / "derivatives"
            / media.id
            / f"{derivative_type}{file_extension}"
        )

    def _persist_derivative(
        self,
        derivative: FotosMediaDerivativeModel,
        *,
        destination_path: Path,
    ) -> tuple[
        FotosMediaDerivativeModel,
        bool,
    ]:
        """Persiste o derivado e remove o arquivo se houver falha."""

        try:
            persisted = self._derivative_repository.add(derivative)
        except Exception:
            if destination_path.exists():
                destination_path.unlink()

            raise

        return persisted, True

    def _cleanup_new_derivatives(
        self,
        derivatives: list[FotosMediaDerivativeModel],
    ) -> None:
        """Remove apenas derivados criados na tentativa atual."""

        for derivative in reversed(derivatives):
            file_path = self._settings.uploads_dir / Path(derivative.storage_key)

            try:
                self._derivative_repository.delete(derivative)
            finally:
                if file_path.exists():
                    file_path.unlink()
