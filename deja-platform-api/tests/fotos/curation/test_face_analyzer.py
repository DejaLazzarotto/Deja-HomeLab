"""Testes do analisador facial independente da persistência."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from deja_platform_api.fotos.curation.analyzer import analyze_faces


def test_analyzer_returns_detections_and_suggestions() -> None:
    media = SimpleNamespace(
        id="media-1",
        organization_id="org-1",
        tenant_id="tenant-1",
        environment_id="env-1",
        media_type="image",
        processing_status="ready",
        deleted_at=None,
    )

    image_path = Path("foto-teste.jpg")
    models_dir = Path("modelos")
    references = [("pessoa-1", Path("referencia.webp"))]

    from PIL import Image

    image = Image.new("RGB", (200, 200))

    with (
        patch(
            "deja_platform_api.fotos.curation.analyzer.engine.detect",
            return_value=[(0.1, 0.2, 0.3, 0.4)],
        ),
        patch(
            "deja_platform_api.fotos.curation.analyzer.engine.suggest",
            return_value=("pessoa-1", 0.85),
        ),
        patch(
            "deja_platform_api.fotos.curation.analyzer.Image.open",
            return_value=image,
        ),
    ):
        result = analyze_faces(media, image_path, references, models_dir)

    assert result.media_id == "media-1"
    assert result.organization_id == "org-1"
    assert result.tenant_id == "tenant-1"
    assert result.environment_id == "env-1"
    assert len(result.detections) == 1

    face = result.detections[0]
    assert face.person_id == "pessoa-1"
    assert face.confidence == pytest.approx(0.85)
    assert face.x == pytest.approx(0.1)


def test_analyzer_rejects_video() -> None:
    media = SimpleNamespace(
        media_type="video",
        processing_status="ready",
        deleted_at=None,
    )

    with pytest.raises(ValueError, match="fotografia pronta"):
        analyze_faces(media, Path("video.mp4"), [], Path("modelos"))
