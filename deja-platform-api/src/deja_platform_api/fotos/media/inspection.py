from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PIL import Image, UnidentifiedImageError


@dataclass(frozen=True)
class FotosImageInspection:
    """Metadados obtidos a partir de uma imagem validada."""

    format: str
    width: int
    height: int
    original_date: datetime | None


class FotosImageInspectionError(Exception):
    """Falha ao validar ou inspecionar uma imagem."""


def inspect_image(
    file_path: Path,
) -> FotosImageInspection:
    """Valida a imagem e extrai metadados básicos."""

    try:
        with Image.open(file_path) as image:
            image.verify()

        with Image.open(file_path) as image:
            width, height = image.size
            image_format = (
                image.format or ""
            ).upper()

            exif = image.getexif()
            original_date = _extract_original_date(
                exif.get(36867)
                or exif.get(36868)
                or exif.get(306)
            )

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:
        raise FotosImageInspectionError(
            "O conteúdo do arquivo não é uma imagem válida."
        ) from exc

    if width <= 0 or height <= 0:
        raise FotosImageInspectionError(
            "A imagem possui dimensões inválidas."
        )

    return FotosImageInspection(
        format=image_format,
        width=width,
        height=height,
        original_date=original_date,
    )


def _extract_original_date(
    value: object,
) -> datetime | None:
    """Converte datas EXIF conhecidas para datetime."""

    if not isinstance(value, str):
        return None

    try:
        return datetime.strptime(
            value,
            "%Y:%m:%d %H:%M:%S",
        )
    except ValueError:
        return None