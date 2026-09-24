"""Contratos da curadoria facial."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

FaceStatus = Literal["unknown", "suggested", "confirmed", "rejected"]


class FaceBox(BaseModel):
    x: float = Field(ge=0, lt=1)
    y: float = Field(ge=0, lt=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def inside_image(self) -> "FaceBox":
        if self.x + self.width > 1.000001 or self.y + self.height > 1.000001:
            raise ValueError("A marcação deve ficar dentro da imagem.")
        return self


class FaceCreate(FaceBox):
    person_id: str | None = None


class FaceDecision(BaseModel):
    person_id: str | None = None


class FaceResponse(FaceBox):
    model_config = ConfigDict(from_attributes=True)

    id: str
    media_id: str
    origin: Literal["detected", "manual"]
    status: FaceStatus
    person_id: str | None
    rejected_person_id: str | None
    confidence: float | None
    created_at: datetime


class FacePage(BaseModel):
    items: list[FaceResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class ReferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    face_id: str
    person_id: str
    created_at: datetime


class ReferencePage(BaseModel):
    items: list[ReferenceResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
