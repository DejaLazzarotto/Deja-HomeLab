"""Estruturas para resultados de reconhecimento facial ainda não persistidos."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FaceDetectionResult:
    x: float
    y: float
    width: float
    height: float
    person_id: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class FaceAnalysisResult:
    media_id: str
    organization_id: str
    tenant_id: str
    environment_id: str
    detections: tuple[FaceDetectionResult, ...]
