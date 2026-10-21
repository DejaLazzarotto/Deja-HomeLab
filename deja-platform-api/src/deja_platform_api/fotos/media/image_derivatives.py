from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

THUMBNAIL_MAX_SIZE = 320
PREVIEW_MAX_SIZE = 1600
DERIVATIVE_CONTENT_TYPE = "image/webp"
DERIVATIVE_EXTENSION = ".webp"


@dataclass(frozen=True)
class FotosImageDerivative:
    """Metadados de um derivado de imagem gerado."""

    derivative_type: str
    file_path: Path
    content_type: str
    file_extension: str
    file_size: int
    width: int
    height: int


class FotosImageDerivativeError(Exception):
    """Falha ao gerar derivado de imagem."""


def generate_image_derivative(
    source_path: Path,
    destination_path: Path,
    *,
    derivative_type: str,
) -> FotosImageDerivative:
    """Gera thumbnail ou preview preservando a proporção."""

    max_size = _resolve_max_size(
        derivative_type
    )

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with Image.open(source_path) as source:
            source.load()

            image = source.convert(
                "RGB"
            )

            image.thumbnail(
                (
                    max_size,
                    max_size,
                ),
                Image.Resampling.LANCZOS,
            )

            width, height = image.size

            if width <= 0 or height <= 0:
                raise FotosImageDerivativeError(
                    "O derivado possui dimensões inválidas."
                )

            image.save(
                destination_path,
                format="WEBP",
                quality=85,
                method=6,
            )

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:
        if destination_path.exists():
            destination_path.unlink()

        raise FotosImageDerivativeError(
            "Não foi possível gerar o derivado da imagem."
        ) from exc

    if not destination_path.exists():
        raise FotosImageDerivativeError(
            "O arquivo derivado não foi gerado."
        )

    file_size = destination_path.stat().st_size

    if file_size <= 0:
        destination_path.unlink(
            missing_ok=True,
        )

        raise FotosImageDerivativeError(
            "O arquivo derivado gerado está vazio."
        )

    return FotosImageDerivative(
        derivative_type=derivative_type,
        file_path=destination_path,
        content_type=DERIVATIVE_CONTENT_TYPE,
        file_extension=DERIVATIVE_EXTENSION,
        file_size=file_size,
        width=width,
        height=height,
    )


def _resolve_max_size(
    derivative_type: str,
) -> int:
    """Retorna o limite de dimensão para o tipo de derivado."""

    if derivative_type == "thumbnail":
        return THUMBNAIL_MAX_SIZE

    if derivative_type == "preview":
        return PREVIEW_MAX_SIZE

    raise FotosImageDerivativeError(
        f"Tipo de derivado não suportado: {derivative_type}."
    )