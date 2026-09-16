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

from deja_indicadores_api.authentication.dependencies import (
    require_roles,
)
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
    FotosMediaDerivativeResponse,
    FotosMediaProcessingStatus,
    FotosMediaResponse,
    FotosMediaType,
)
from deja_indicadores_api.module_management.dependencies import (
    require_module,
)
from deja_indicadores_api.user_management.models import (
    UserRole,
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
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
            UserRole.VIEWER,
        )
    ),
]


FotosMediaOperator = Annotated[
    AuthenticatedUser,
    Depends(
        require_roles(
            UserRole.PLATFORM_ADMIN,
            UserRole.ORGANIZATION_ADMIN,
            UserRole.TENANT_ADMIN,
            UserRole.MANAGER,
            UserRole.ANALYST,
        )
    ),
]


@router.get(
    "",
    response_model=list[FotosMediaResponse],
)
def list_media(
    service: FotosMediaServiceDependency,
    current_user: FotosMediaReader,
    organization_id: str | None = Query(default=None),
    tenant_id: str | None = Query(default=None),
    environment_id: str | None = Query(default=None),
    album_id: str | None = Query(default=None),
    media_type: Annotated[FotosMediaType | None, Query()] = None,
    processing_status: Annotated[FotosMediaProcessingStatus | None, Query()] = None,
) -> list[FotosMediaResponse]:
    """Lista mídias autorizadas pelos filtros informados."""

    return service.list(
        current_user=current_user,
        organization_id=organization_id,
        tenant_id=tenant_id,
        environment_id=environment_id,
        album_id=album_id,
        media_type=media_type,
        processing_status=processing_status,
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
    current_user: FotosMediaOperator,
) -> None:
    """Realiza exclusão lógica de uma mídia."""

    service.delete(
        media_id,
        current_user,
    )
