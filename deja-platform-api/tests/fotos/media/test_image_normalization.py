from PIL import Image

from deja_platform_api.fotos.media.image_normalization import (
    normalize_image,
)
from deja_platform_api.fotos.media.inspection import (
    inspect_image,
)


def read_webp_frame_durations(file_path):
    """Lê durações diretamente dos blocos ANMF do WebP."""
    data = file_path.read_bytes()

    assert data[:4] == b"RIFF"
    assert data[8:12] == b"WEBP"

    durations = []
    offset = 12

    while offset + 8 <= len(data):
        chunk_type = data[offset:offset + 4]
        chunk_size = int.from_bytes(
            data[offset + 4:offset + 8],
            "little",
        )

        payload_start = offset + 8
        payload_end = payload_start + chunk_size

        assert payload_end <= len(data)

        if chunk_type == b"ANMF":
            assert chunk_size >= 16
            durations.append(
                int.from_bytes(
                    data[payload_start + 12:payload_start + 15],
                    "little",
                )
            )

        offset = payload_end + (chunk_size % 2)

    assert offset == len(data)

    return durations

def test_animated_gif_is_normalized_to_animated_webp(tmp_path):
    source_path = tmp_path / "animated.gif"

    frames = [
        Image.new("RGB", (40, 30), color)
        for color in ("red", "green", "blue")
    ]

    frames[0].save(
        source_path,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=[100, 200, 300],
        loop=0,
    )

    inspection = inspect_image(source_path)

    assert inspection.is_animated is True

    result = normalize_image(source_path, inspection)

    assert result.content_type == "image/webp"
    assert result.file_extension == ".webp"
    assert result.was_converted is True
    assert result.file_path.is_file()

    with Image.open(result.file_path) as normalized:
        assert normalized.format == "WEBP"
        assert normalized.n_frames == 3
        assert normalized.is_animated is True
        assert normalized.info.get("loop") == 0

        assert read_webp_frame_durations(result.file_path) == [100, 200, 300]


def test_animated_gif_preserves_transparency_and_disposal(tmp_path):
    """Compara os quadros compostos do GIF com o WebP convertido."""
    from PIL import ImageChops, ImageDraw

    source_path = tmp_path / "transparent.gif"

    frames = []
    for index, color in enumerate(("red", "green", "blue")):
        frame = Image.new("RGBA", (48, 36), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)
        left = 4 + index * 12
        draw.rectangle(
            (left, 8, left + 11, 23),
            fill=color,
        )
        frames.append(frame)

    frames[0].save(
        source_path,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=[100, 200, 300],
        loop=0,
        disposal=[1, 2, 3],
        transparency=0,
        optimize=False,
    )

    original_frames = []
    with Image.open(source_path) as original:
        assert original.n_frames == 3

        for index in range(original.n_frames):
            original.seek(index)
            original_frames.append(original.convert("RGBA").copy())

    inspection = inspect_image(source_path)
    assert inspection.is_animated is True

    result = normalize_image(source_path, inspection)

    with Image.open(result.file_path) as normalized:
        assert normalized.n_frames == len(original_frames)

        for index, expected in enumerate(original_frames):
            normalized.seek(index)
            actual = normalized.convert("RGBA")
            difference = ImageChops.difference(expected, actual)

            assert difference.getbbox() is None, (
                f"Quadro {index} diferente após conversão"
            )

def test_animated_webp_preserves_all_frames(tmp_path):
    source_path = tmp_path / "animated.webp"

    frames = [
        Image.new("RGB", (40, 30), color)
        for color in ("red", "green", "blue")
    ]

    frames[0].save(
        source_path,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=[100, 200, 300],
        loop=0,
        lossless=True,
    )

    inspection = inspect_image(source_path)

    assert inspection.is_animated is True

    result = normalize_image(source_path, inspection)

    assert result.content_type == "image/webp"
    assert result.file_extension == ".webp"
    assert result.file_path.is_file()

    with Image.open(result.file_path) as normalized:
        assert normalized.format == "WEBP"
        assert normalized.n_frames == 3
        assert normalized.is_animated is True
        assert normalized.info.get("loop") == 0

        assert read_webp_frame_durations(result.file_path) == [100, 200, 300]


def test_animated_gif_source_survives_conversion_failure(
    tmp_path,
    monkeypatch,
):
    source_path = tmp_path / "animated.gif"

    frames = [
        Image.new("RGB", (40, 30), color)
        for color in ("red", "green", "blue")
    ]

    frames[0].save(
        source_path,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=[100, 200, 300],
        loop=0,
    )

    original_content = source_path.read_bytes()
    inspection = inspect_image(source_path)

    original_save = Image.Image.save

    def failing_save(self, fp, *args, **kwargs):
        if kwargs.get("format") == "WEBP":
            raise OSError("Simulated WebP conversion failure")
        return original_save(self, fp, *args, **kwargs)

    monkeypatch.setattr(Image.Image, "save", failing_save)

    import pytest

    from deja_platform_api.fotos.media.image_normalization import (
        FotosImageNormalizationError,
    )

    with pytest.raises(FotosImageNormalizationError):
        normalize_image(source_path, inspection)

    assert source_path.is_file()
    assert source_path.read_bytes() == original_content
    assert not (tmp_path / "normalized.webp").exists()