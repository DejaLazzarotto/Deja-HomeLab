from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FotosMediaType = Literal[
    "image",
    "video",
]

FotosMediaProcessingStatus = Literal[
    "received",
    "validating",
    "processing",
    "ready",
    "failed",
    "quarantine",
]


class FotosMediaResponse(BaseModel):
    """Representação pública de uma mídia do Deja Fotos."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str

    organization_id: str
    tenant_id: str
    environment_id: str

    album_id: str | None

    original_name: str
    media_type: FotosMediaType
    content_type: str
    file_extension: str | None
    file_size: int
    checksum_sha256: str

    processing_status: FotosMediaProcessingStatus
    processing_error: str | None

    original_date: datetime | None

    width: int | None
    height: int | None
    duration_seconds: float | None

    view_count: int

    created_by_user_id: str | None

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class FotosMediaListFilters(BaseModel):
    """Filtros aceitos na listagem de mídias."""

    organization_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )

    tenant_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )

    environment_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )

    album_id: str | None = Field(
        default=None,
        min_length=36,
        max_length=36,
    )

    media_type: FotosMediaType | None = None

    processing_status: FotosMediaProcessingStatus | None = None

    include_deleted: bool = False