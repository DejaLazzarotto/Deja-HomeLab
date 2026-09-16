import subprocess
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from deja_indicadores_api.fotos.media.video_inspection import (
    FotosVideoInspection,
    FotosVideoInspectionError,
    inspect_video,
)

NORMALIZED_VIDEO_CONTENT_TYPE = "video/mp4"
NORMALIZED_VIDEO_EXTENSION = ".mp4"
COMPATIBLE_VIDEO_CODEC = "h264"
COMPATIBLE_AUDIO_CODECS = {
    None,
    "aac",
}
FILE_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class FotosNormalizedVideo:
    """Resultado gerenciado da normalização de um vídeo."""

    file_path: Path
    content_type: str
    file_extension: str
    file_size: int
    checksum_sha256: str
    was_converted: bool
    width: int
    height: int
    duration_seconds: float


class FotosVideoNormalizationError(Exception):
    """Falha ao normalizar um vídeo recebido."""


def normalize_video(
    source_path: Path,
    *,
    source_extension: str | None,
    inspection: FotosVideoInspection,
    ffmpeg_executable: str,
    ffprobe_executable: str,
    timeout_seconds: int,
) -> FotosNormalizedVideo:
    """Preserva MP4 compatível ou converte o vídeo para MP4."""

    if _is_compatible_mp4(
        source_extension=source_extension,
        inspection=inspection,
    ):
        return FotosNormalizedVideo(
            file_path=source_path,
            content_type=NORMALIZED_VIDEO_CONTENT_TYPE,
            file_extension=NORMALIZED_VIDEO_EXTENSION,
            file_size=_resolve_file_size(
                source_path
            ),
            checksum_sha256=_calculate_checksum(
                source_path
            ),
            was_converted=False,
            width=inspection.width,
            height=inspection.height,
            duration_seconds=inspection.duration_seconds,
        )

    destination_path = (
        source_path.parent
        / "normalized.mp4"
    )

    command = [
        ffmpeg_executable,
        "-y",
        "-i",
        str(source_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        "-map_metadata",
        "0",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
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
            timeout=timeout_seconds,
        )
    except (
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoNormalizationError(
            "Não foi possível executar a conversão do vídeo."
        ) from exc

    if result.returncode != 0:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoNormalizationError(
            "Não foi possível converter o vídeo para MP4."
        )

    try:
        normalized_inspection = inspect_video(
            destination_path,
            ffprobe_executable=ffprobe_executable,
        )
    except FotosVideoInspectionError as exc:
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoNormalizationError(
            "O vídeo MP4 convertido é inválido."
        ) from exc

    if not _is_compatible_mp4(
        source_extension=NORMALIZED_VIDEO_EXTENSION,
        inspection=normalized_inspection,
    ):
        _cleanup_destination(
            destination_path
        )

        raise FotosVideoNormalizationError(
            "O vídeo convertido não possui codecs compatíveis."
        )

    return FotosNormalizedVideo(
        file_path=destination_path,
        content_type=NORMALIZED_VIDEO_CONTENT_TYPE,
        file_extension=NORMALIZED_VIDEO_EXTENSION,
        file_size=_resolve_file_size(
            destination_path
        ),
        checksum_sha256=_calculate_checksum(
            destination_path
        ),
        was_converted=True,
        width=normalized_inspection.width,
        height=normalized_inspection.height,
        duration_seconds=normalized_inspection.duration_seconds,
    )


def _is_compatible_mp4(
    *,
    source_extension: str | None,
    inspection: FotosVideoInspection,
) -> bool:
    """Verifica compatibilidade para reprodução ampla do MP4."""

    return (
        source_extension == NORMALIZED_VIDEO_EXTENSION
        and inspection.video_codec == COMPATIBLE_VIDEO_CODEC
        and inspection.audio_codec in COMPATIBLE_AUDIO_CODECS
    )


def _resolve_file_size(
    file_path: Path,
) -> int:
    """Valida e retorna o tamanho de um vídeo."""

    if not file_path.is_file():
        raise FotosVideoNormalizationError(
            "O arquivo de vídeo normalizado não foi encontrado."
        )

    file_size = file_path.stat().st_size

    if file_size <= 0:
        raise FotosVideoNormalizationError(
            "O arquivo de vídeo normalizado está vazio."
        )

    return file_size


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


def _cleanup_destination(
    destination_path: Path,
) -> None:
    """Remove uma conversão parcial, quando existente."""

    destination_path.unlink(
        missing_ok=True,
    )