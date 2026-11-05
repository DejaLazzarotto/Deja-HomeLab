"""Regressão do cache de referências faciais em memória."""

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image

from deja_platform_api.fotos.curation import engine


def test_reference_embeddings_are_reused_and_invalidated(tmp_path: Path) -> None:
    reference = tmp_path / "reference.png"
    Image.new("RGB", (64, 64), "white").save(reference)
    detector = tmp_path / "detector.onnx"
    recognizer_model = tmp_path / "recognizer.onnx"
    detector.write_bytes(b"detector")
    recognizer_model.write_bytes(b"recognizer")

    recognizer = Mock()
    recognizer.match.return_value = 0.91
    cv2 = SimpleNamespace(FaceRecognizerSF_FR_COSINE=0)
    feature = Mock(return_value=object())
    engine._reference_feature.cache_clear()

    try:
        with (
            patch.object(engine, "_cv2", return_value=cv2),
            patch.object(engine, "_feature", feature),
            patch.object(
                cv2,
                "FaceRecognizerSF",
                SimpleNamespace(create=Mock(return_value=recognizer)),
                create=True,
            ),
        ):
            args = (
                object(),
                [("person-1", reference)],
                cv2,
                detector,
                recognizer,
                recognizer_model,
            )
            assert engine._best_match(*args) == ("person-1", 0.91)
            assert engine._best_match(*args) == ("person-1", 0.91)
            assert feature.call_count == 1

            # Alterar a imagem deve recalcular sua característica facial.
            stat = reference.stat()
            os.utime(
                reference,
                ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000),
            )
            assert engine._best_match(*args) == ("person-1", 0.91)
            assert feature.call_count == 2

            # Trocar o modelo também invalida o cache.
            stat = recognizer_model.stat()
            os.utime(
                recognizer_model,
                ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000_000),
            )
            assert engine._best_match(*args) == ("person-1", 0.91)
            assert feature.call_count == 3
    finally:
        engine._reference_feature.cache_clear()


def test_deleted_reference_is_not_matched_from_cache(tmp_path: Path) -> None:
    reference = tmp_path / "missing.png"
    detector = tmp_path / "detector.onnx"
    recognizer_model = tmp_path / "recognizer.onnx"
    detector.write_bytes(b"detector")
    recognizer_model.write_bytes(b"recognizer")
    recognizer = Mock()
    cv2 = SimpleNamespace(FaceRecognizerSF_FR_COSINE=0)

    assert engine._best_match(
        object(),
        [("person-1", reference)],
        cv2,
        detector,
        recognizer,
        recognizer_model,
    ) is None
    recognizer.match.assert_not_called()
