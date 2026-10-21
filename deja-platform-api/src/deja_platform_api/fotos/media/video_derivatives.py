import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

POSTER_MAX_SIZE = 1600
POSTER_CONTENT_TYPE = "image/webp"
POSTER_EXTENSION = ".webp"

VIDEO_PREVIEW_MAX_WIDTH = 1280
VIDEO_PREVIEW_MAX_HEIGHT = 720
VIDEO_PREVIEW_CONTENT_TYPE = "video/mp4"
VIDEO_PREVIEW_EXTENSION = ".mp4"


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

    width, height = _inspect_generated_image(
        destination_path
    )

    return FotosVideoDerivative(
        derivative_type="poster",
        file_path=destination_path,
        content_type=POSTER_CONTENT_TYPE,
        file_extension=POSTER_EXTENSION,
        file_size=_resolve_file_size(
            destination_path
        ),
        width=width,
        height=height,
    )


def generate_video_preview(
    source_path: Path,
    destination_path: Path,
    *,
    ffmpeg_executable: str,
    width: int,
    height: int,
) -> FotosVideoDerivative:
    """Gera uma cópia MP4 reduzida para reprodução e navegação."""

    if width <= 0 or height <= 0:
        raise FotosVideoDerivativeError(
            "O vídeo possui dimensões inválidas."
        )

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        ffmpeg_executable,
        "-y",
        "-i",
        str(source_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        (
            "scale="
            f"'min({VIDEO_PREVIEW_MAX_WIDTH},iw)':"
            f"'min({VIDEO_PREVIEW_MAX_HEIGHT},ih)':"
            "force_original_aspect_ratio=decrease:"
            "force_divisible_by=2"
        ),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        "-sn",
        "-dn",
        str(destination_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
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
            "Não foi possível gerar o preview do vídeo."
        )

    file_size = _resolve_file_size(
        destination_path
    )

    preview_width, preview_height = (
        _calculate_preview_dimensions(
            width,
            height,
        )
    )

    return FotosVideoDerivative(
        derivative_type="preview",
        file_path=destination_path,
        content_type=VIDEO_PREVIEW_CONTENT_TYPE,
        file_extension=VIDEO_PREVIEW_EXTENSION,
        file_size=file_size,
        width=preview_width,
        height=preview_height,
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


def _inspect_generated_image(
    destination_path: Path,
) -> tuple[int, int]:
    """Valida a imagem derivada e retorna suas dimensões."""

    _resolve_file_size(
        destination_path
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

    return width, height


def _resolve_file_size(
    destination_path: Path,
) -> int:
    """Valida a existência e o tamanho do arquivo derivado."""

    if not destination_path.exists():
        raise FotosVideoDerivativeError(
            "O arquivo derivado não foi gerado."
        )

    file_size = destination_path.stat().st_size

    if file_size <= 0:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoDerivativeError(
            "O arquivo derivado gerado está vazio."
        )

    return file_size


def _calculate_preview_dimensions(
    width: int,
    height: int,
) -> tuple[int, int]:
    """Calcula dimensões do preview preservando proporção e pares."""

    scale = min(
        VIDEO_PREVIEW_MAX_WIDTH / width,
        VIDEO_PREVIEW_MAX_HEIGHT / height,
        1.0,
    )

    preview_width = max(
        2,
        int(width * scale) // 2 * 2,
    )
    preview_height = max(
        2,
        int(height * scale) // 2 * 2,
    )

    return (
        preview_width,
        preview_height,
    )


def _cleanup_destination(
    destination_path: Path,
) -> None:
    """Remove um arquivo parcial de derivado, quando existente."""

    destination_path.unlink(
        missing_ok=True,
    )