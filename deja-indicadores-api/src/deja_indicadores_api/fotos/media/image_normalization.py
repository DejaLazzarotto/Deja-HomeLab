from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from deja_indicadores_api.fotos.media.inspection import (
    FotosImageInspection,
)

PRESERVED_IMAGE_FORMATS = {
    "JPEG": (
        "image/jpeg",
        ".jpg",
    ),
    "PNG": (
        "image/png",
        ".png",
    ),
    "WEBP": (
        "image/webp",
        ".webp",
    ),
    "GIF": (
        "image/gif",
        ".gif",
    ),
}

CONVERTED_IMAGE_FORMATS = {
    "BMP",
}

FILE_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class FotosNormalizedImage:
    """Resultado gerenciado da normalização de uma imagem."""

    file_path: Path
    content_type: str
    file_extension: str
    file_size: int
    checksum_sha256: str
    was_converted: bool
    width: int
    height: int


class FotosImageNormalizationError(Exception):
    """Falha ao normalizar uma imagem recebida."""


def normalize_image(
    source_path: Path,
    inspection: FotosImageInspection,
) -> FotosNormalizedImage:
    """Preserva formatos aceitos ou converte a imagem para PNG."""

    preserved_format = PRESERVED_IMAGE_FORMATS.get(
        inspection.format
    )

    if preserved_format is not None:
        content_type, file_extension = preserved_format

        return FotosNormalizedImage(
            file_path=source_path,
            content_type=content_type,
            file_extension=file_extension,
            file_size=source_path.stat().st_size,
            checksum_sha256=_calculate_checksum(
                source_path
            ),
            was_converted=False,
            width=inspection.width,
            height=inspection.height,
        )

    if inspection.format not in CONVERTED_IMAGE_FORMATS:
        raise FotosImageNormalizationError(
            "O formato real da imagem não é suportado."
        )

    destination_path = (
        source_path.parent
        / "normalized.png"
    )

    try:
        with Image.open(source_path) as source:
            source.load()

            normalized = ImageOps.exif_transpose(
                source
            )

            has_alpha = (
                "A" in normalized.getbands()
                or (
                    normalized.mode == "P"
                    and "transparency"
                    in normalized.info
                )
            )

            converted = normalized.convert(
                "RGBA" if has_alpha else "RGB"
            )

            converted.save(
                destination_path,
                format="PNG",
                optimize=True,
            )

        if (
            not destination_path.exists()
            or not destination_path.is_file()
        ):
            raise FotosImageNormalizationError(
                "O arquivo PNG normalizado não foi gerado."
            )

        file_size = destination_path.stat().st_size

        if file_size <= 0:
            raise FotosImageNormalizationError(
                "O arquivo PNG normalizado está vazio."
            )

        source_path.unlink()

        return FotosNormalizedImage(
            file_path=destination_path,
            content_type="image/png",
            file_extension=".png",
            file_size=file_size,
            checksum_sha256=_calculate_checksum(
                destination_path
            ),
            was_converted=True,
            width=converted.width,
            height=converted.height,
        )

    except FotosImageNormalizationError:
        if destination_path.exists():
            destination_path.unlink()

        raise

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:
        if destination_path.exists():
            destination_path.unlink()

        raise FotosImageNormalizationError(
            "Não foi possível converter a imagem para PNG."
        ) from exc


def _calculate_checksum(
    file_path: Path,
) -> str:
    """Calcula o SHA-256 do arquivo informado."""

    digest = sha256()

    with file_path.open("rb") as source:
        while chunk := source.read(
            FILE_CHUNK_SIZE
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()