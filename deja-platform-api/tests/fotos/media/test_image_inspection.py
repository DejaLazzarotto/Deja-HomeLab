from pathlib import Path

import pytest
from PIL import Image

from deja_platform_api.fotos.media.inspection import inspect_image


@pytest.mark.parametrize(
    ("image_format", "extension"),
    [
        ("JPEG", ".jpg"),
        ("PNG", ".png"),
        ("WEBP", ".webp"),
    ],
)
def test_inspect_static_image(
    tmp_path: Path,
    image_format: str,
    extension: str,
) -> None:
    path = tmp_path / f"static{extension}"

    Image.new("RGB", (40, 30), "red").save(
        path,
        format=image_format,
    )

    result = inspect_image(path)

    assert result.format == image_format
    assert result.width == 40
    assert result.height == 30
    assert result.is_animated is False


@pytest.mark.parametrize(
    ("image_format", "extension"),
    [
        ("GIF", ".gif"),
        ("WEBP", ".webp"),
    ],
)
def test_inspect_animated_image(
    tmp_path: Path,
    image_format: str,
    extension: str,
) -> None:
    path = tmp_path / f"animated{extension}"

    frames = [
        Image.new("RGB", (40, 30), color)
        for color in ("red", "green", "blue")
    ]

    frames[0].save(
        path,
        format=image_format,
        save_all=True,
        append_images=frames[1:],
        duration=[100, 200, 300],
        loop=0,
        lossless=True if image_format == "WEBP" else False,
    )

    result = inspect_image(path)

    assert result.format == image_format
    assert result.width == 40
    assert result.height == 30
    assert result.is_animated is True

    with Image.open(path) as image:
        assert image.n_frames == 3
