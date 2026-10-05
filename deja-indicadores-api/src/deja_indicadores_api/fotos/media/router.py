from datetime import datetime
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    Path,
    Query,
    UploadFile,
)
from fastapi import status as http_status
from fastapi.responses import FileResponse

from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.fotos.media.background_processing import (
    process_media_in_background,
)
from deja_indicadores_api.fotos.media.dependencies import (
    FotosMediaDerivativeServiceDependency,
    FotosMediaServiceDependency,
    FotosMediaSessionFactoryDependency,
    SettingsDependency,
)
from deja_indicadores_api.fotos.media.schemas import (
    FotosMediaBulkResponse,
    FotosMediaBulkUpdate,
    FotosMediaDerivativeResponse,
    FotosMediaDescriptionUpdate,
    FotosMediaListResponse,
    FotosMediaOriginalDateUpdate,
    FotosMediaPeriodResponse,
    FotosMediaProcessingStatus,
    FotosMediaResponse,
    FotosMediaType,
)
from deja_indicadores_api.module_management.dependencies import (
    require_module,
    require_module_roles,
)
from deja_indicadores_api.user_management.models import (
    UserModuleRole,
)

router = APIRouter(
    prefix="/fotos/media",
    tags=["Deja Fotos - Mídias"],
    dependencies=[Depends(require_module("fotos"))],
)


MediaId = Annotated[
    str,
    Path(
        min_length=36,
        max_length=36,
        description="Identificador UUID da mídia.",
    ),
]


EnvironmentIdForm = Annotated[
    str,
    Form(
        min_length=36,
        max_length=36,
    ),
]


AlbumIdForm = Annotated[
    str | None,
    Form(),
]


MediaFile = Annotated[
    UploadFile,
    File(),
]


FotosMediaReader = Annotated[
    AuthenticatedUser,
    Depends(
        require_module_roles(
            "fotos",
            UserModuleRole.MANAGER,
            UserModuleRole.VIEWER,
        )
    ),
]


FotosMediaManager = Annotated[
    AuthenticatedUser,
    Depends(
        require_module_roles(
            "fotos",
            UserModuleRole.MANAGER,
        )
    ),
]


FotosMediaOperator = Annotated[
    AuthenticatedUser,
    Depends(
        require_module_roles(
            "fotos",
            UserModuleRole.MANAGER,
        )
    ),
]


@router.get(
    "",
    response_model=FotosMediaListResponse,
)
def list_media(
    service: FotosMediaServiceDependency,
    current_user: FotosMediaReader,
    organization_id: str | None = Query(default=None),
    tenant_id: str | None = Query(default=None),
    environment_id: str | None = Query(default=None),
    album_id: str | None = Query(default=None),
    media_type: Annotated[FotosMediaType | None, Query()] = None,
    processing_status: Annotated[
        FotosMediaProcessingStatus | None,
        Query(),
    ] = None,
    original_date_from: Annotated[
        datetime | None,
        Query(),
    ] = None,
    original_date_to: Annotated[
        datetime | None,
        Query(),
    ] = None,
    original_year: int | None = Query(
        default=None,
        ge=1,
        le=9999,
    ),
    original_month: int | None = Query(
        default=None,
        ge=1,
        le=12,
    ),
    without_original_date: bool = Query(default=False),
    original_date_verified: bool | None = Query(default=None),
    original_date_conflict: bool | None = Query(default=None),
    was_converted: bool | None = Query(default=None),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
) -> FotosMediaListResponse:
    """Lista uma página de mídias autorizadas pelos filtros."""

    items, total = service.list(
        current_user=current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        album_id=album_id,
        media_type=media_type,
        processing_status=processing_status,
        original_date_from=original_date_from,
        original_date_to=original_date_to,
        original_year=original_year,
        original_month=original_month,
        without_original_date=without_original_date,
        original_date_verified=original_date_verified,
        original_date_conflict=original_date_conflict,
        was_converted=was_converted,
        page=page,
        page_size=page_size,
    )

    total_pages = (
        total + page_size - 1
    ) // page_size

    return FotosMediaListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/periods",
    response_model=list[FotosMediaPeriodResponse],
)
def list_media_periods(
    service: FotosMediaServiceDependency,
    current_user: FotosMediaReader,
    organization_id: str | None = Query(default=None),
    tenant_id: str | None = Query(default=None),
    environment_id: str | None = Query(default=None),
) -> list[FotosMediaPeriodResponse]:
    """Lista os períodos reais existentes no acervo autorizado."""

    return service.list_periods(
        current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
    )

@router.patch(
    "/bulk",
    response_model=FotosMediaBulkResponse,
)
def bulk_update_media(
    payload: FotosMediaBulkUpdate,
    service: FotosMediaServiceDependency,
    current_user: FotosMediaManager,
) -> FotosMediaBulkResponse:
    """Executa uma operação administrativa em lote."""

    return service.bulk_update(
        payload,
        current_user,
    )


@router.get(
    "/{media_id}",
    response_model=FotosMediaResponse,
)
def get_media(
    media_id: MediaId,
    service: FotosMediaServiceDependency,
    current_user: FotosMediaReader,
) -> FotosMediaResponse:
    """Consulta uma mídia pelo identificador."""

    return service.find_by_id(
        media_id,
        current_user,
    )


@router.patch(
    "/{media_id}/original-date",
    response_model=FotosMediaResponse,
)
def update_media_original_date(
    media_id: MediaId,
    payload: FotosMediaOriginalDateUpdate,
    service: FotosMediaServiceDependency,
    current_user: FotosMediaManager,
) -> FotosMediaResponse:
    """Confirma manualmente a data original da mídia."""

    return service.update_original_date(
        media_id,
        payload.original_date,
        current_user,
    )


@router.patch(
    "/{media_id}/description",
    response_model=FotosMediaResponse,
)
def update_media_description(
    media_id: MediaId,
    payload: FotosMediaDescriptionUpdate,
    service: FotosMediaServiceDependency,
    current_user: FotosMediaOperator,
) -> FotosMediaResponse:
    """Atualiza a descrição de uma mídia de vídeo."""

    return service.update_description(
        media_id,
        payload.description,
        current_user,
    )


@router.post(
    "",
    response_model=FotosMediaResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def upload_media(
    background_tasks: BackgroundTasks,
    service: FotosMediaServiceDependency,
    session_factory: FotosMediaSessionFactoryDependency,
    settings: SettingsDependency,
    current_user: FotosMediaOperator,
    environment_id: EnvironmentIdForm,
    file: MediaFile,
    album_id: AlbumIdForm = None,
) -> FotosMediaResponse:
    """Recebe, armazena e agenda o processamento de uma mídia original."""

    media = await service.create_from_upload(
        environment_id=environment_id,
        album_id=album_id,
        file=file,
        current_user=current_user,
    )

    background_tasks.add_task(
        process_media_in_background,
        media.id,
        session_factory=session_factory,
        settings=settings,
    )

    return media


@router.post(
    "/{media_id}/process",
    response_model=FotosMediaResponse,
)
def process_media(
    media_id: MediaId,
    service: FotosMediaServiceDependency,
    derivative_service: FotosMediaDerivativeServiceDependency,
    current_user: FotosMediaOperator,
) -> FotosMediaResponse:
    """Processa os arquivos derivados de uma mídia."""

    media = service.find_by_id(
        media_id,
        current_user,
    )

    derivative_service.process(media)

    return media


@router.get(
    "/{media_id}/derivatives",
    response_model=list[FotosMediaDerivativeResponse],
)
def list_media_derivatives(
    media_id: MediaId,
    service: FotosMediaServiceDependency,
    derivative_service: FotosMediaDerivativeServiceDependency,
    current_user: FotosMediaReader,
) -> list[FotosMediaDerivativeResponse]:
    """Lista os derivados disponíveis de uma mídia autorizada."""

    service.find_by_id(
        media_id,
        current_user,
    )

    return derivative_service.list_derivatives(media_id)


@router.get(
    "/{media_id}/thumbnail",
)
def get_media_thumbnail(
    media_id: MediaId,
    service: FotosMediaServiceDependency,
    derivative_service: FotosMediaDerivativeServiceDependency,
    current_user: FotosMediaReader,
) -> FileResponse:
    """Retorna o thumbnail WebP de uma mídia autorizada."""

    service.find_by_id(
        media_id,
        current_user,
    )

    file_path, derivative = derivative_service.get_derivative_file(
        media_id,
        "thumbnail",
    )

    return FileResponse(
        path=file_path,
        media_type=derivative.content_type,
    )


@router.get(
    "/{media_id}/preview",
)
def get_media_preview(
    media_id: MediaId,
    service: FotosMediaServiceDependency,
    derivative_service: FotosMediaDerivativeServiceDependency,
    current_user: FotosMediaReader,
) -> FileResponse:
    """Retorna o preview de uma mídia autorizada."""

    service.find_by_id(
        media_id,
        current_user,
    )

    file_path, derivative = derivative_service.get_derivative_file(
        media_id,
        "preview",
    )

    return FileResponse(
        path=file_path,
        media_type=derivative.content_type,
    )


@router.get(
    "/{media_id}/poster",
)
def get_media_poster(
    media_id: MediaId,
    service: FotosMediaServiceDependency,
    derivative_service: FotosMediaDerivativeServiceDependency,
    current_user: FotosMediaReader,
) -> FileResponse:
    """Retorna o poster de uma mídia de vídeo autorizada."""

    service.find_by_id(
        media_id,
        current_user,
    )

    file_path, derivative = derivative_service.get_derivative_file(
        media_id,
        "poster",
    )

    return FileResponse(
        path=file_path,
        media_type=derivative.content_type,
    )


@router.get(
    "/{media_id}/original",
)
def get_media_original(
    media_id: MediaId,
    service: FotosMediaServiceDependency,
    current_user: FotosMediaReader,
) -> FileResponse:
    """Retorna o arquivo original de uma mídia autorizada."""

    file_path, media = service.get_original_file(
        media_id,
        current_user,
    )

    download_name = (
        f"{FilePath(media.original_name).stem}"
        f"{media.file_extension or ''}"
    )

    return FileResponse(
        path=file_path,
        media_type=media.content_type,
        filename=download_name,
    )


@router.delete(
    "/{media_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
def delete_media(
    media_id: MediaId,
    service: FotosMediaServiceDependency,
    current_user: FotosMediaManager,
) -> None:
    """Exclui a mídia e seus arquivos sem remover pessoas ou outras mídias."""

    service.delete(
        media_id,
        current_user,
    )