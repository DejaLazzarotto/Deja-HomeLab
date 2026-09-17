from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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

FotosMediaOriginalDateSource = Literal[
    "embedded_metadata",
    "source_folder",
    "filename",
    "filesystem",
    "manual",
    "ai_suggested",
]

FotosMediaBulkOperation = Literal[
    "set_original_date",
    "verify_original_date",
    "clear_original_date_conflict",
    "set_album",
]

FotosMediaIdentifier = Annotated[
    str,
    Field(
        min_length=36,
        max_length=36,
    ),
]


class FotosMediaOriginalDateUpdate(BaseModel):
    """Correção manual da data original de uma mídia."""

    original_date: datetime


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

    source_content_type: str
    source_file_extension: str | None
    source_file_size: int
    source_checksum_sha256: str

    media_type: FotosMediaType
    content_type: str
    file_extension: str | None
    file_size: int
    checksum_sha256: str
    was_converted: bool

    processing_status: FotosMediaProcessingStatus
    processing_error: str | None

    original_date: datetime | None
    original_date_source: FotosMediaOriginalDateSource | None
    original_date_verified: bool
    original_date_conflict: bool

    width: int | None
    height: int | None
    duration_seconds: float | None

    view_count: int

    created_by_user_id: str | None

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class FotosMediaListResponse(BaseModel):
    """Página de mídias do Deja Fotos."""

    items: list[FotosMediaResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class FotosMediaBulkUpdateBase(BaseModel):
    """Campos comuns das operações administrativas em lote."""

    media_ids: list[FotosMediaIdentifier] = Field(
        min_length=1,
        max_length=100,
    )

    @field_validator("media_ids")
    @classmethod
    def validate_unique_media_ids(
        cls,
        media_ids: list[str],
    ) -> list[str]:
        """Rejeita identificadores repetidos no mesmo lote."""

        if len(media_ids) != len(set(media_ids)):
            raise ValueError(
                "Os identificadores das mídias devem ser únicos."
            )

        return media_ids


class FotosMediaBulkSetOriginalDate(
    FotosMediaBulkUpdateBase
):
    """Aplica uma data original manual ao lote."""

    operation: Literal["set_original_date"]
    original_date: datetime


class FotosMediaBulkVerifyOriginalDate(
    FotosMediaBulkUpdateBase
):
    """Confirma as datas originais já existentes."""

    operation: Literal["verify_original_date"]


class FotosMediaBulkClearOriginalDateConflict(
    FotosMediaBulkUpdateBase
):
    """Limpa conflitos de data sem confirmar a data."""

    operation: Literal["clear_original_date_conflict"]


class FotosMediaBulkSetAlbum(
    FotosMediaBulkUpdateBase
):
    """Associa o lote a um álbum ou remove sua associação."""

    operation: Literal["set_album"]
    album_id: FotosMediaIdentifier | None


FotosMediaBulkUpdate = Annotated[
    FotosMediaBulkSetOriginalDate
    | FotosMediaBulkVerifyOriginalDate
    | FotosMediaBulkClearOriginalDateConflict
    | FotosMediaBulkSetAlbum,
    Field(discriminator="operation"),
]


class FotosMediaBulkItemResult(BaseModel):
    """Resultado individual de uma operação em lote."""

    media_id: str
    success: bool
    media: FotosMediaResponse | None = None
    error_code: str | None = None
    error_message: str | None = None


class FotosMediaBulkResponse(BaseModel):
    """Resultado consolidado de uma operação em lote."""

    operation: FotosMediaBulkOperation
    requested_count: int
    succeeded_count: int
    failed_count: int
    results: list[FotosMediaBulkItemResult]


class FotosMediaDerivativeResponse(BaseModel):
    """Representação pública de um derivado de mídia."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    derivative_type: str
    content_type: str
    file_extension: str | None
    file_size: int
    width: int | None
    height: int | None
    created_at: datetime


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

    original_date_from: datetime | None = None
    original_date_to: datetime | None = None

    original_year: int | None = Field(
        default=None,
        ge=1,
        le=9999,
    )

    original_month: int | None = Field(
        default=None,
        ge=1,
        le=12,
    )

    without_original_date: bool = False
    original_date_verified: bool | None = None
    original_date_conflict: bool | None = None
    was_converted: bool | None = None

    include_deleted: bool = False

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=50,
        ge=1,
        le=200,
    )