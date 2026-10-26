"""Análise facial independente da persistência de resultados."""

from pathlib import Path

from PIL import Image, ImageOps

from deja_platform_api.fotos.curation import engine
from deja_platform_api.fotos.curation.analysis_models import (
    FaceAnalysisResult,
    FaceDetectionResult,
)
from deja_platform_api.fotos.media.models import FotosMediaModel


def analyze_faces(
    media: FotosMediaModel,
    image_path: Path,
    references: list[tuple[str, Path]],
    models_dir: Path,
) -> FaceAnalysisResult:
    """Detecta rostos e sugere identidades sem modificar o banco."""

    if media.media_type != "image" or media.processing_status != "ready":
        raise ValueError("A análise facial exige uma fotografia pronta.")

    if media.deleted_at is not None:
        raise ValueError("Não é permitido analisar uma fotografia excluída.")

    boxes = engine.detect(image_path, models_dir)
    detections = []

    with Image.open(image_path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        width, height = image.size

        for x, y, box_width, box_height in boxes:
            person_id = None
            confidence = None

            if references:
                crop = image.crop(
                    (
                        round(x * width),
                        round(y * height),
                        round((x + box_width) * width),
                        round((y + box_height) * height),
                    )
                )

                match = engine.suggest(crop, references, models_dir)

                if match is None:
                    match = engine.suggest_in_image(
                        image_path,
                        (x, y, box_width, box_height),
                        references,
                        models_dir,
                    )

                if match is not None:
                    person_id, confidence = match

            detections.append(
                FaceDetectionResult(
                    x=x,
                    y=y,
                    width=box_width,
                    height=box_height,
                    person_id=person_id,
                    confidence=confidence,
                )
            )

    return FaceAnalysisResult(
        media_id=media.id,
        organization_id=media.organization_id,
        tenant_id=media.tenant_id,
        environment_id=media.environment_id,
        detections=tuple(detections),
    )
