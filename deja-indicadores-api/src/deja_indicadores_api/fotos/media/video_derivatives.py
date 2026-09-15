import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

POSTER_MAX_SIZE = 1600
POSTER_CONTENT_TYPE = "image/webp"
POSTER_EXTENSION = ".webp"


@dataclass(frozen=True)
class FotosVideoDerivative:
    """Metadados de um derivado de vídeo gerado."""

    derivative_type: str
    file_path: Path
    content_type: str
    file_extension: str
    file_size: int
    width: int
    height: int


class FotosVideoDerivativeError(Exception):
    """Falha ao gerar derivado de vídeo."""


def generate_video_poster(
    source_path: Path,
    destination_path: Path,
    *,
    ffmpeg_executable: str,
    duration_seconds: float,
) -> FotosVideoDerivative:
    """Gera um poster WebP a partir de um frame do vídeo."""

    if duration_seconds <= 0:
        raise FotosVideoDerivativeError(
            "A duração do vídeo é inválida."
        )

    seek_seconds = _resolve_seek_seconds(
        duration_seconds
    )

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        ffmpeg_executable,
        "-y",
        "-ss",
        f"{seek_seconds:.3f}",
        "-i",
        str(source_path),
        "-frames:v",
        "1",
        "-vf",
        (
            "scale="
            f"'min({POSTER_MAX_SIZE},iw)':"
            f"'min({POSTER_MAX_SIZE},ih)':"
            "force_original_aspect_ratio=decrease"
        ),
        "-c:v",
        "libwebp",
        "-quality",
        "85",
        str(destination_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except (
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoDerivativeError(
            "Não foi possível executar o ffmpeg."
        ) from exc

    if result.returncode != 0:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoDerivativeError(
            "Não foi possível gerar o poster do vídeo."
        )

    if not destination_path.exists():
        raise FotosVideoDerivativeError(
            "O arquivo de poster não foi gerado."
        )

    file_size = destination_path.stat().st_size

    if file_size <= 0:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoDerivativeError(
            "O arquivo de poster gerado está vazio."
        )

    try:
        with Image.open(destination_path) as image:
            image.load()

            width, height = image.size

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoDerivativeError(
            "O poster gerado não é uma imagem válida."
        ) from exc

    if width <= 0 or height <= 0:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoDerivativeError(
            "O poster gerado possui dimensões inválidas."
        )

    return FotosVideoDerivative(
        derivative_type="poster",
        file_path=destination_path,
        content_type=POSTER_CONTENT_TYPE,
        file_extension=POSTER_EXTENSION,
        file_size=file_size,
        width=width,
        height=height,
    )


def _resolve_seek_seconds(
    duration_seconds: float,
) -> float:
    """Escolhe um frame representativo próximo de 10% do vídeo."""

    seek_seconds = duration_seconds * 0.10

    if duration_seconds <= 1:
        return max(
            duration_seconds * 0.5,
            0.01,
        )

    return min(
        max(
            seek_seconds,
            1.0,
        ),
        max(
            duration_seconds - 0.1,
            0.01,
        ),
    )


def _cleanup_destination(
    destination_path: Path,
) -> None:
    """Remove um arquivo parcial de poster, quando existente."""

    destination_path.unlink(
        missing_ok=True,
    )