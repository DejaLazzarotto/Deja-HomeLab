from pathlib import Path
from uuid import uuid4

from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.fotos.media.derivative_models import (
    FotosMediaDerivativeModel,
)
from deja_indicadores_api.fotos.media.derivative_repository import (
    FotosMediaDerivativeRepository,
)
from deja_indicadores_api.fotos.media.image_derivatives import (
    generate_image_derivative,
)
from deja_indicadores_api.fotos.media.models import (
    FotosMediaModel,
)
from deja_indicadores_api.fotos.media.repository import (
    FotosMediaRepository,
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

    def process_image(
        self,
        media: FotosMediaModel,
    ) -> list[FotosMediaDerivativeModel]:
        """Gera thumbnail e preview de uma imagem."""

        if media.media_type != "image":
            raise ValueError(
                "A mídia informada não é uma imagem."
            )

        original_path = (
            self._settings.uploads_dir
            / Path(media.original_storage_key)
        )

        if (
            not original_path.exists()
            or not original_path.is_file()
        ):
            raise FileNotFoundError(
                "O arquivo original da mídia não foi encontrado."
            )

        media.processing_status = "processing"
        media.processing_error = None

        self._media_repository.update(
            media
        )

        derivatives: list[
            FotosMediaDerivativeModel
        ] = []

        newly_created: list[
            FotosMediaDerivativeModel
        ] = []

        try:
            for derivative_type in (
                "thumbnail",
                "preview",
            ):
                (
                    derivative,
                    was_created,
                ) = self._generate_derivative(
                    media,
                    original_path=original_path,
                    derivative_type=derivative_type,
                )

                derivatives.append(
                    derivative
                )

                if was_created:
                    newly_created.append(
                        derivative
                    )

        except Exception as exc:
            self._cleanup_new_derivatives(
                newly_created
            )

            media.processing_status = "failed"
            media.processing_error = str(exc)

            self._media_repository.update(
                media
            )

            raise

        media.processing_status = "ready"
        media.processing_error = None

        self._media_repository.update(
            media
        )

        return derivatives

    def get_derivative_file(
        self,
        media_id: str,
        derivative_type: str,
    ) -> tuple[
        Path,
        FotosMediaDerivativeModel,
    ]:
        """Retorna o arquivo físico de um derivado existente."""

        derivative = (
            self._derivative_repository.find_by_media_and_type(
                media_id,
                derivative_type,
            )
        )

        if derivative is None:
            raise FileNotFoundError(
                "O derivado solicitado não foi encontrado."
            )

        file_path = (
            self._settings.uploads_dir
            / Path(derivative.storage_key)
        )

        if (
            not file_path.exists()
            or not file_path.is_file()
        ):
            raise FileNotFoundError(
                "O arquivo físico do derivado não foi encontrado."
            )

        return file_path, derivative

    def _generate_derivative(
        self,
        media: FotosMediaModel,
        *,
        original_path: Path,
        derivative_type: str,
    ) -> tuple[
        FotosMediaDerivativeModel,
        bool,
    ]:
        """Gera e persiste um derivado individual."""

        existing = (
            self._derivative_repository.find_by_media_and_type(
                media.id,
                derivative_type,
            )
        )

        if existing is not None:
            return existing, False

        storage_key = (
            Path("fotos")
            / media.organization_id
            / media.tenant_id
            / media.environment_id
            / "derivatives"
            / media.id
            / f"{derivative_type}.webp"
        )

        destination_path = (
            self._settings.uploads_dir
            / storage_key
        )

        generated = generate_image_derivative(
            original_path,
            destination_path,
            derivative_type=derivative_type,
        )

        derivative = FotosMediaDerivativeModel(
            id=str(
                uuid4()
            ),
            media_id=media.id,
            derivative_type=derivative_type,
            storage_key=storage_key.as_posix(),
            content_type=generated.content_type,
            file_extension=generated.file_extension,
            file_size=generated.file_size,
            width=generated.width,
            height=generated.height,
        )

        try:
            persisted = self._derivative_repository.add(
                derivative
            )
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

        for derivative in reversed(
            derivatives
        ):
            file_path = (
                self._settings.uploads_dir
                / Path(derivative.storage_key)
            )

            try:
                self._derivative_repository.delete(
                    derivative
                )
            finally:
                if file_path.exists():
                    file_path.unlink()