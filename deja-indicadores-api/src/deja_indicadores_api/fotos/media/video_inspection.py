import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FotosVideoInspection:
    """Metadados obtidos a partir de um vídeo validado."""

    width: int
    height: int
    duration_seconds: float
    video_codec: str | None
    audio_codec: str | None


class FotosVideoInspectionError(Exception):
    """Falha ao validar ou inspecionar um vídeo."""


def inspect_video(
    file_path: Path,
    *,
    ffprobe_executable: str,
) -> FotosVideoInspection:
    """Valida o vídeo e extrai metadados com ffprobe."""

    command = [
        ffprobe_executable,
        "-v",
        "error",
        "-show_entries",
        (
            "format=duration:"
            "stream=index,codec_type,codec_name,width,height"
        ),
        "-of",
        "json",
        str(file_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        raise FotosVideoInspectionError(
            "Não foi possível executar o ffprobe."
        ) from exc

    if result.returncode != 0:
        raise FotosVideoInspectionError(
            "O conteúdo do arquivo não é um vídeo válido."
        )

    try:
        payload = json.loads(
            result.stdout,
        )
    except json.JSONDecodeError as exc:
        raise FotosVideoInspectionError(
            "O ffprobe retornou dados inválidos."
        ) from exc

    streams = payload.get(
        "streams",
        [],
    )

    video_stream = next(
        (
            stream
            for stream in streams
            if stream.get("codec_type") == "video"
        ),
        None,
    )

    if video_stream is None:
        raise FotosVideoInspectionError(
            "Nenhuma faixa de vídeo válida foi encontrada."
        )

    width = video_stream.get(
        "width"
    )
    height = video_stream.get(
        "height"
    )

    if (
        not isinstance(width, int)
        or not isinstance(height, int)
        or width <= 0
        or height <= 0
    ):
        raise FotosVideoInspectionError(
            "O vídeo possui dimensões inválidas."
        )

    format_data = payload.get(
        "format",
        {},
    )

    try:
        duration_seconds = float(
            format_data.get(
                "duration",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise FotosVideoInspectionError(
            "Não foi possível determinar a duração do vídeo."
        ) from exc

    if duration_seconds <= 0:
        raise FotosVideoInspectionError(
            "O vídeo possui duração inválida."
        )

    audio_stream = next(
        (
            stream
            for stream in streams
            if stream.get("codec_type") == "audio"
        ),
        None,
    )

    return FotosVideoInspection(
        width=width,
        height=height,
        duration_seconds=duration_seconds,
        video_codec=video_stream.get(
            "codec_name"
        ),
        audio_codec=(
            audio_stream.get(
                "codec_name"
            )
            if audio_stream is not None
            else None
        ),
    )