import logging
import re
import shutil
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.core.exceptions import ApplicationError
from deja_indicadores_api.fotos.albums.models import (
    FotosAlbumModel,
)
from deja_indicadores_api.fotos.albums.repository import (
    FotosAlbumRepository,
)
from deja_indicadores_api.fotos.media.derivative_models import (
    FotosMediaDerivativeModel,
)
from deja_indicadores_api.fotos.media.derivative_repository import (
    FotosMediaDerivativeRepository,
)
from deja_indicadores_api.fotos.media.exceptions import (
    FotosMediaAlbumNotFoundError,
    FotosMediaAlbumScopeMismatchError,
    FotosMediaDeletionConflictError,
    FotosMediaDescriptionNotSupportedError,
    FotosMediaDuplicateError,
    FotosMediaEmptyFileError,
    FotosMediaFileNotFoundError,
    FotosMediaInvalidContentError,
    FotosMediaInvalidTypeError,
    FotosMediaNotFoundError,
    FotosMediaOriginalDateMissingError,
    FotosMediaStorageConflictError,
    FotosMediaStorageMoveError,
    FotosMediaTooLargeError,
)
from deja_indicadores_api.fotos.media.image_normalization import (
    FotosImageNormalizationError,
    normalize_image,
)
from deja_indicadores_api.fotos.media.inspection import (
    FotosImageInspectionError,
    inspect_image,
)
from deja_indicadores_api.fotos.media.models import (
    FotosMediaModel,
)
from deja_indicadores_api.fotos.media.repository import (
    FotosMediaRepository,
)
from deja_indicadores_api.fotos.media.schemas import (
    FotosMediaBulkClearOriginalDateConflict,
    FotosMediaBulkItemResult,
    FotosMediaBulkResponse,
    FotosMediaBulkSetAlbum,
    FotosMediaBulkSetOriginalDate,
    FotosMediaBulkUpdate,
    FotosMediaBulkVerifyOriginalDate,
)
from deja_indicadores_api.fotos.media.storage import (
    build_derivative_storage_key,
    build_original_storage_key,
)
from deja_indicadores_api.fotos.media.video_inspection import (
    FotosVideoInspectionError,
    inspect_video,
)
from deja_indicadores_api.tenant_management.exceptions import (
    EnvironmentNotFoundError,
    TenantNotFoundError,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    TenantModel,
)
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)
from deja_indicadores_api.user_management.models import (
    UserModuleRole,
)

FOTOS_MODULE_KEY = "fotos"

FOTOS_MEDIA_READER_ROLES = frozenset(
    {
        UserModuleRole.MANAGER,
        UserModuleRole.VIEWER,
    }
)

FOTOS_MEDIA_OPERATOR_ROLES = frozenset(
    {
        UserModuleRole.MANAGER,
    }
)

FOTOS_MEDIA_MANAGER_ROLES = frozenset(
    {
        UserModuleRole.MANAGER,
    }
)

ALLOWED_FOTOS_CONTENT_TYPES = {
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    "image/gif": "image",
    "image/bmp": "image",
    "image/x-ms-bmp": "image",
    "video/mp4": "video",
    "video/quicktime": "video",
    "video/mpeg": "video",
}

UPLOAD_CHUNK_SIZE = 1024 * 1024

FILENAME_DATE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?P<date>(?:19|20)\d{6})"
    r"(?:[-_](?P<time>\d{6}))?"
    r"(?!\d)"
)

logger = logging.getLogger(__name__)


def infer_original_date_from_filename(
    filename: str,
) -> tuple[datetime, str] | None:
    """Infere data e precisão a partir de nomes reconhecíveis."""

    match = FILENAME_DATE_PATTERN.search(Path(filename).stem)

    if match is None:
        return None

    date_part = match.group("date")
    time_part = match.group("time")

    try:
        if time_part is not None:
            return (
                datetime.strptime(
                    date_part + time_part,
                    "%Y%m%d%H%M%S",
                ),
                "datetime",
            )

        return (
            datetime.strptime(
                date_part,
                "%Y%m%d",
            ),
            "date",
        )
    except ValueError:
        return None


class FotosMediaService:
    """Regras de aplicação das mídias do Deja Fotos."""

    def __init__(
        self,
        repository: FotosMediaRepository,
        album_repository: FotosAlbumRepository,
        derivative_repository: FotosMediaDerivativeRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._album_repository = album_repository
        self._derivative_repository = derivative_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._authorization_service = authorization_service
        self._settings = settings

    def list(
        self,
        current_user: AuthenticatedUser,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        album_id: str | None = None,
        media_type: str | None = None,
        processing_status: str | None = None,
        original_date_from: datetime | None = None,
        original_date_to: datetime | None = None,
        original_year: int | None = None,
        original_month: int | None = None,
        without_original_date: bool = False,
        original_date_verified: bool | None = None,
        original_date_conflict: bool | None = None,
        was_converted: bool | None = None,
        include_deleted: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[FotosMediaModel], int]:
        """Lista uma página de mídias dentro do escopo permitido."""

        self._require_roles(
            current_user,
            FOTOS_MEDIA_READER_ROLES,
        )

        (
            effective_organization_id,
            effective_tenant_id,
            effective_environment_id,
        ) = self._authorization_service.resolve_list_scope(
            current_user,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )

        if album_id is not None:
            album = self._require_album(
                album_id,
            )
            self._require_album_matches_scope(
                album,
                organization_id=effective_organization_id,
                tenant_id=effective_tenant_id,
                environment_id=effective_environment_id,
            )

        normalized_original_date_from = self._normalize_datetime(
            original_date_from,
        )
        normalized_original_date_to = self._normalize_datetime(
            original_date_to,
        )

        return self._repository.list(
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
            album_id=album_id,
            media_type=media_type,
            processing_status=processing_status,
            original_date_from=normalized_original_date_from,
            original_date_to=normalized_original_date_to,
            original_year=original_year,
            original_month=original_month,
            without_original_date=without_original_date,
            original_date_verified=original_date_verified,
            original_date_conflict=original_date_conflict,
            was_converted=was_converted,
            include_deleted=include_deleted,
            page=page,
            page_size=page_size,
        )

    def find_by_id(
        self,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> FotosMediaModel:
        """Retorna uma mídia dentro do escopo permitido."""

        self._require_roles(
            current_user,
            FOTOS_MEDIA_READER_ROLES,
        )

        media = self._require_media(
            media_id,
        )

        self._authorization_service.require_scope(
            current_user,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
        )

        return media

    async def create_from_upload(
        self,
        *,
        environment_id: str,
        album_id: str | None,
        file: UploadFile,
        current_user: AuthenticatedUser,
    ) -> FotosMediaModel:
        """Armazena o original, valida o conteúdo e registra a mídia."""

        self._require_roles(
            current_user,
            FOTOS_MEDIA_OPERATOR_ROLES,
        )

        environment = self._require_environment(
            environment_id,
        )
        tenant = self._require_tenant(
            environment.tenant_id,
        )

        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )

        if album_id is not None:
            album = self._require_album(
                album_id,
            )

            self._require_album_matches_scope(
                album,
                organization_id=tenant.organization_id,
                tenant_id=tenant.id,
                environment_id=environment.id,
            )

        source_content_type = file.content_type or "application/octet-stream"

        media_type = ALLOWED_FOTOS_CONTENT_TYPES.get(source_content_type)

        if media_type is None:
            raise FotosMediaInvalidTypeError(
                source_content_type,
            )

        original_name = Path(file.filename or "arquivo").name

        source_extension = Path(original_name).suffix.lower()

        media_id = str(uuid4())

        staging_key = (
            Path("fotos")
            / tenant.organization_id
            / tenant.id
            / environment.id
            / ".staging"
            / media_id
            / f"source{source_extension}"
        )

        file_path = self._settings.uploads_dir / staging_key

        staging_directory = file_path.parent

        staging_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        max_size_bytes = self._settings.fotos_media_max_size_mb * 1024 * 1024

        digest = sha256()
        total_size = 0

        width: int | None = None
        height: int | None = None
        duration_seconds: float | None = None
        original_date: datetime | None = None
        original_date_source: str | None = None
        original_date_precision: str | None = None

        try:
            with file_path.open("wb") as destination:
                while True:
                    chunk = await file.read(UPLOAD_CHUNK_SIZE)

                    if not chunk:
                        break

                    total_size += len(chunk)

                    if total_size > max_size_bytes:
                        raise FotosMediaTooLargeError(
                            self._settings.fotos_media_max_size_mb,
                        )

                    digest.update(chunk)
                    destination.write(chunk)

            if total_size == 0:
                raise FotosMediaEmptyFileError()

            source_checksum = digest.hexdigest()

            existing_media = self._repository.find_by_source_checksum(
                source_checksum,
                environment_id=environment.id,
            )

            if existing_media is not None:
                if existing_media.deleted_at is None:
                    raise FotosMediaDuplicateError(
                        existing_media.id,
                    )

                if file_path.exists():
                    file_path.unlink()

                try:
                    staging_directory.rmdir()
                except OSError:
                    pass

                return self._restore_deleted_media(
                    existing_media,
                    album_id=album_id,
                    original_name=original_name,
                )

            managed_content_type = source_content_type
            managed_extension = source_extension
            managed_file_size = total_size
            managed_checksum = source_checksum
            was_converted = False

            if media_type == "image":
                try:
                    inspection = inspect_image(
                        file_path,
                    )
                    normalized = normalize_image(
                        file_path,
                        inspection,
                    )
                except (
                    FotosImageInspectionError,
                    FotosImageNormalizationError,
                ) as exc:
                    raise FotosMediaInvalidContentError(
                        str(exc),
                    ) from exc

                file_path = normalized.file_path
                managed_content_type = normalized.content_type
                managed_extension = normalized.file_extension
                managed_file_size = normalized.file_size
                managed_checksum = normalized.checksum_sha256
                was_converted = normalized.was_converted
                width = normalized.width
                height = normalized.height
                original_date = inspection.original_date

            elif media_type == "video":
                try:
                    inspection = inspect_video(
                        file_path,
                        ffprobe_executable=(self._settings.ffprobe_executable),
                    )
                except FotosVideoInspectionError as exc:
                    raise FotosMediaInvalidContentError(
                        str(exc),
                    ) from exc

                width = inspection.width
                height = inspection.height
                duration_seconds = inspection.duration_seconds
                original_date = inspection.original_date

            if original_date is not None:
                original_date_source = "embedded_metadata"
                original_date_precision = "datetime"
            else:
                inferred_date = infer_original_date_from_filename(
                    original_name,
                )

                if inferred_date is not None:
                    (
                        original_date,
                        original_date_precision,
                    ) = inferred_date
                    original_date_source = "filename"

            storage_key = build_original_storage_key(
                organization_id=tenant.organization_id,
                tenant_id=tenant.id,
                environment_id=environment.id,
                media_id=media_id,
                file_extension=managed_extension,
                original_date=original_date,
            )

            destination_path = self._settings.uploads_dir / storage_key

            destination_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_path.replace(
                destination_path,
            )
            file_path = destination_path

            try:
                staging_directory.rmdir()
            except OSError:
                pass

        except Exception:
            if file_path.exists():
                file_path.unlink()

            try:
                staging_directory.rmdir()
            except OSError:
                pass

            raise

        media = FotosMediaModel(
            id=media_id,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
            album_id=album_id,
            original_name=original_name,
            source_content_type=source_content_type,
            source_file_extension=source_extension or None,
            source_file_size=total_size,
            source_checksum_sha256=source_checksum,
            media_type=media_type,
            content_type=managed_content_type,
            file_extension=managed_extension or None,
            file_size=managed_file_size,
            checksum_sha256=managed_checksum,
            was_converted=was_converted,
            original_storage_key=storage_key.as_posix(),
            processing_status="received",
            processing_error=None,
            original_date=original_date,
            original_date_source=original_date_source,
            original_date_precision=original_date_precision,
            original_date_verified=False,
            original_date_conflict=False,
            width=width,
            height=height,
            duration_seconds=duration_seconds,
            view_count=0,
            created_by_user_id=current_user.id,
        )

        try:
            return self._repository.add(
                media,
            )
        except Exception:
            if file_path.exists():
                file_path.unlink()

            raise

    def _restore_deleted_media(
        self,
        media: FotosMediaModel,
        *,
        album_id: str | None,
        original_name: str,
    ) -> FotosMediaModel:
        """Restaura uma mídia e aplica data inferida quando cabível."""

        previous_album_id = media.album_id
        previous_original_name = media.original_name
        previous_processing_status = media.processing_status
        previous_processing_error = media.processing_error
        previous_deleted_at = media.deleted_at
        previous_original_date = media.original_date
        previous_original_date_source = media.original_date_source
        previous_original_date_precision = media.original_date_precision
        previous_storage_key = media.original_storage_key

        current_path = self._settings.uploads_dir / Path(media.original_storage_key)
        target_path = current_path
        moved_original = False

        if media.original_date is None:
            inferred_date = infer_original_date_from_filename(
                original_name,
            )

            if inferred_date is not None:
                (
                    inferred_value,
                    inferred_precision,
                ) = inferred_date

                target_storage_key = build_original_storage_key(
                    organization_id=media.organization_id,
                    tenant_id=media.tenant_id,
                    environment_id=media.environment_id,
                    media_id=media.id,
                    file_extension=(media.file_extension or current_path.suffix),
                    original_date=inferred_value,
                )

                target_path = self._settings.uploads_dir / target_storage_key

                if target_path != current_path:
                    if not current_path.exists() or not current_path.is_file():
                        raise FotosMediaFileNotFoundError(
                            media.id,
                        )

                    if target_path.exists() or target_path.parent.exists():
                        raise FotosMediaStorageConflictError(
                            media.id,
                        )

                    try:
                        target_path.parent.mkdir(
                            parents=True,
                            exist_ok=False,
                        )
                        current_path.replace(
                            target_path,
                        )
                        moved_original = True
                    except FileExistsError as error:
                        raise FotosMediaStorageConflictError(
                            media.id,
                        ) from error
                    except OSError as error:
                        if target_path.parent.exists():
                            try:
                                target_path.parent.rmdir()
                            except OSError:
                                pass

                        raise FotosMediaStorageMoveError(
                            media.id,
                        ) from error

                    try:
                        current_path.parent.rmdir()
                    except OSError:
                        pass

                media.original_date = inferred_value
                media.original_date_source = "filename"
                media.original_date_precision = inferred_precision
                media.original_storage_key = target_storage_key.as_posix()

        media.deleted_at = None
        media.album_id = album_id
        media.original_name = original_name
        media.processing_status = "received"
        media.processing_error = None

        try:
            return self._repository.update(
                media,
            )
        except Exception:
            media.album_id = previous_album_id
            media.original_name = previous_original_name
            media.processing_status = previous_processing_status
            media.processing_error = previous_processing_error
            media.deleted_at = previous_deleted_at
            media.original_date = previous_original_date
            media.original_date_source = previous_original_date_source
            media.original_date_precision = previous_original_date_precision
            media.original_storage_key = previous_storage_key

            if moved_original:
                try:
                    current_path.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )
                    target_path.replace(
                        current_path,
                    )

                    try:
                        target_path.parent.rmdir()
                    except OSError:
                        pass
                except OSError as error:
                    raise FotosMediaStorageMoveError(
                        media.id,
                    ) from error

            raise

    def get_original_file(
        self,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> tuple[
        Path,
        FotosMediaModel,
    ]:
        """Retorna o arquivo original de uma mídia autorizada."""

        media = self.find_by_id(
            media_id,
            current_user,
        )

        file_path = self._settings.uploads_dir / Path(media.original_storage_key)

        if not file_path.exists() or not file_path.is_file():
            raise FotosMediaFileNotFoundError(
                media.id,
            )

        return file_path, media

    def update_original_date(
        self,
        media_id: str,
        original_date: datetime,
        current_user: AuthenticatedUser,
    ) -> FotosMediaModel:
        """Corrige a data e reorganiza o original gerenciado."""

        self._require_roles(
            current_user,
            FOTOS_MEDIA_MANAGER_ROLES,
        )

        media = self._require_media_for_update(
            media_id,
        )

        try:
            self._authorization_service.require_scope(
                current_user,
                organization_id=media.organization_id,
                tenant_id=media.tenant_id,
                environment_id=media.environment_id,
            )

            return self._set_original_date(
                media,
                original_date,
            )
        except Exception:
            self._repository.rollback()
            raise

    def update_description(
        self,
        media_id: str,
        description: str | None,
        current_user: AuthenticatedUser,
    ) -> FotosMediaModel:
        """Atualiza a descrição editável de uma mídia de vídeo."""

        self._require_roles(
            current_user,
            FOTOS_MEDIA_OPERATOR_ROLES,
        )

        media = self._require_media_for_update(
            media_id,
        )

        try:
            self._authorization_service.require_scope(
                current_user,
                organization_id=media.organization_id,
                tenant_id=media.tenant_id,
                environment_id=media.environment_id,
            )

            if media.media_type != "video":
                raise FotosMediaDescriptionNotSupportedError(
                    media.id,
                )

            media.description = description

            return self._repository.update(
                media,
            )
        except Exception:
            self._repository.rollback()
            raise

    def bulk_update(
        self,
        payload: FotosMediaBulkUpdate,
        current_user: AuthenticatedUser,
    ) -> FotosMediaBulkResponse:
        """Executa uma operação administrativa sobre várias mídias."""

        self._require_roles(
            current_user,
            FOTOS_MEDIA_MANAGER_ROLES,
        )

        results: list[FotosMediaBulkItemResult] = []

        for media_id in payload.media_ids:
            try:
                media = self._bulk_update_item(
                    media_id,
                    payload,
                    current_user,
                )
            except ApplicationError as error:
                self._repository.rollback()
                results.append(
                    FotosMediaBulkItemResult(
                        media_id=media_id,
                        success=False,
                        error_code=error.error_code,
                        error_message=error.message,
                    )
                )
            except Exception:
                self._repository.rollback()
                logger.exception(
                    "Falha inesperada na operação em lote da mídia %s.",
                    media_id,
                )
                results.append(
                    FotosMediaBulkItemResult(
                        media_id=media_id,
                        success=False,
                        error_code="fotos_media_bulk_item_failed",
                        error_message=("Não foi possível atualizar a mídia."),
                    )
                )
            else:
                results.append(
                    FotosMediaBulkItemResult(
                        media_id=media_id,
                        success=True,
                        media=media,
                    )
                )

        succeeded_count = sum(result.success for result in results)

        return FotosMediaBulkResponse(
            operation=payload.operation,
            requested_count=len(payload.media_ids),
            succeeded_count=succeeded_count,
            failed_count=(len(payload.media_ids) - succeeded_count),
            results=results,
        )

    def _bulk_update_item(
        self,
        media_id: str,
        payload: FotosMediaBulkUpdate,
        current_user: AuthenticatedUser,
    ) -> FotosMediaModel:
        """Executa a operação solicitada sobre uma mídia bloqueada."""

        media = self._require_media_for_update(
            media_id,
        )

        self._authorization_service.require_scope(
            current_user,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
        )

        if isinstance(
            payload,
            FotosMediaBulkSetOriginalDate,
        ):
            return self._set_original_date(
                media,
                payload.original_date,
            )

        if isinstance(
            payload,
            FotosMediaBulkVerifyOriginalDate,
        ):
            return self._verify_original_date(
                media,
            )

        if isinstance(
            payload,
            FotosMediaBulkClearOriginalDateConflict,
        ):
            return self._clear_original_date_conflict(
                media,
            )

        if isinstance(
            payload,
            FotosMediaBulkSetAlbum,
        ):
            return self._set_album(
                media,
                payload.album_id,
            )

        raise ValueError("Operação em lote não suportada.")

    def _set_original_date(
        self,
        media: FotosMediaModel,
        original_date: datetime,
    ) -> FotosMediaModel:
        """Aplica a data manual e reorganiza todos os arquivos da mídia."""

        normalized_date = self._normalize_datetime(
            original_date,
        )

        if normalized_date is None:
            raise ValueError("A data original é obrigatória.")

        current_storage_key = Path(media.original_storage_key)
        current_path = self._settings.uploads_dir / current_storage_key

        if not current_path.exists() or not current_path.is_file():
            raise FotosMediaFileNotFoundError(
                media.id,
            )

        target_storage_key = build_original_storage_key(
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            media_id=media.id,
            file_extension=media.file_extension or "",
            original_date=normalized_date,
        )
        target_path = self._settings.uploads_dir / target_storage_key

        derivatives = self._derivative_repository.list_by_media_id(
            media.id,
        )
        derivative_targets: list[
            tuple[
                FotosMediaDerivativeModel,
                str,
                Path,
                Path,
                Path,
            ]
        ] = []

        for derivative in derivatives:
            derivative_current_key = Path(derivative.storage_key)
            derivative_current_path = self._settings.uploads_dir / derivative_current_key
            derivative_target_key = build_derivative_storage_key(
                organization_id=media.organization_id,
                tenant_id=media.tenant_id,
                environment_id=media.environment_id,
                media_id=media.id,
                derivative_type=(derivative.derivative_type),
                file_extension=(derivative_current_key.suffix),
                original_date=normalized_date,
            )
            derivative_target_path = self._settings.uploads_dir / derivative_target_key

            derivative_targets.append(
                (
                    derivative,
                    derivative.storage_key,
                    derivative_current_path,
                    derivative_target_path,
                    derivative_target_key,
                )
            )

        if target_path != current_path:
            if target_path.exists() or target_path.parent.exists():
                raise FotosMediaStorageConflictError(
                    media.id,
                )

        for (
            _,
            _,
            derivative_current_path,
            derivative_target_path,
            _,
        ) in derivative_targets:
            if (
                derivative_target_path != derivative_current_path
                and derivative_target_path.exists()
            ):
                raise FotosMediaStorageConflictError(
                    media.id,
                )

        original_moved = False
        moved_derivatives: list[tuple[Path, Path]] = []

        try:
            if target_path != current_path:
                target_path.parent.mkdir(
                    parents=True,
                    exist_ok=False,
                )
                current_path.replace(
                    target_path,
                )
                original_moved = True

            for (
                _,
                _,
                derivative_current_path,
                derivative_target_path,
                _,
            ) in derivative_targets:
                if (
                    derivative_target_path == derivative_current_path
                    or not derivative_current_path.is_file()
                ):
                    continue

                derivative_target_path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                derivative_current_path.replace(
                    derivative_target_path,
                )
                moved_derivatives.append(
                    (
                        derivative_current_path,
                        derivative_target_path,
                    )
                )
        except FileExistsError as error:
            self._rollback_storage_moves(
                current_path=current_path,
                target_path=target_path,
                original_moved=original_moved,
                moved_derivatives=moved_derivatives,
            )

            raise FotosMediaStorageConflictError(
                media.id,
            ) from error
        except OSError as error:
            self._rollback_storage_moves(
                current_path=current_path,
                target_path=target_path,
                original_moved=original_moved,
                moved_derivatives=moved_derivatives,
            )

            raise FotosMediaStorageMoveError(
                media.id,
            ) from error

        previous_original_date = media.original_date
        previous_original_date_source = media.original_date_source
        previous_original_date_precision = media.original_date_precision
        previous_original_date_verified = media.original_date_verified
        previous_original_date_conflict = media.original_date_conflict
        previous_storage_key = media.original_storage_key

        media.original_date = normalized_date
        media.original_date_source = "manual"
        media.original_date_precision = "datetime"
        media.original_date_verified = True
        media.original_date_conflict = False
        media.original_storage_key = target_storage_key.as_posix()

        for (
            derivative,
            _,
            _,
            _,
            derivative_target_key,
        ) in derivative_targets:
            derivative.storage_key = derivative_target_key.as_posix()

        try:
            return self._repository.update(
                media,
            )
        except Exception:
            media.original_date = previous_original_date
            media.original_date_source = previous_original_date_source
            media.original_date_precision = previous_original_date_precision
            media.original_date_verified = previous_original_date_verified
            media.original_date_conflict = previous_original_date_conflict
            media.original_storage_key = previous_storage_key

            for (
                derivative,
                previous_derivative_key,
                _,
                _,
                _,
            ) in derivative_targets:
                derivative.storage_key = previous_derivative_key

            try:
                self._rollback_storage_moves(
                    current_path=current_path,
                    target_path=target_path,
                    original_moved=original_moved,
                    moved_derivatives=moved_derivatives,
                )
            except OSError as error:
                raise FotosMediaStorageMoveError(
                    media.id,
                ) from error

            raise

        finally:
            self._remove_empty_storage_parents(
                current_path.parent,
            )

            for (
                derivative_current_path,
                _,
            ) in moved_derivatives:
                self._remove_empty_storage_parents(
                    derivative_current_path.parent,
                )

    def _rollback_storage_moves(
        self,
        *,
        current_path: Path,
        target_path: Path,
        original_moved: bool,
        moved_derivatives: list[tuple[Path, Path]],
    ) -> None:
        """Desfaz movimentações físicas ainda não consolidadas."""

        for (
            derivative_current_path,
            derivative_target_path,
        ) in reversed(moved_derivatives):
            if not derivative_target_path.exists():
                continue

            derivative_current_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            derivative_target_path.replace(
                derivative_current_path,
            )

        if original_moved and target_path.exists():
            current_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            target_path.replace(
                current_path,
            )

    @staticmethod
    def _remove_empty_storage_parents(
        directory: Path,
    ) -> None:
        """Remove somente diretórios vazios abaixo da raiz de uploads."""

        current = directory

        for _ in range(3):
            try:
                current.rmdir()
            except OSError:
                break

            current = current.parent

    def _verify_original_date(
        self,
        media: FotosMediaModel,
    ) -> FotosMediaModel:
        """Confirma a data existente e encerra seu conflito."""

        if media.original_date is None:
            raise FotosMediaOriginalDateMissingError(
                media.id,
            )

        media.original_date_verified = True
        media.original_date_conflict = False

        return self._repository.update(
            media,
        )

    def _clear_original_date_conflict(
        self,
        media: FotosMediaModel,
    ) -> FotosMediaModel:
        """Limpa o conflito sem alterar a confirmação existente."""

        media.original_date_conflict = False

        return self._repository.update(
            media,
        )

    def _set_album(
        self,
        media: FotosMediaModel,
        album_id: str | None,
    ) -> FotosMediaModel:
        """Associa a mídia a um álbum ou remove sua associação."""

        if album_id is not None:
            album = self._require_album(
                album_id,
            )
            self._require_album_matches_scope(
                album,
                organization_id=media.organization_id,
                tenant_id=media.tenant_id,
                environment_id=media.environment_id,
            )

        media.album_id = album_id

        return self._repository.update(
            media,
        )

    def delete(
        self,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Remove uma mídia e seus arquivos, preservando pessoas e outras mídias."""

        self._require_roles(
            current_user,
            FOTOS_MEDIA_MANAGER_ROLES,
        )

        media = self._require_media(
            media_id,
        )

        self._authorization_service.require_scope(
            current_user,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
        )

        locked = self._repository.find_by_id_for_update(media.id)
        if locked is None:
            raise FotosMediaNotFoundError(media_id)
        if locked.processing_status == "processing":
            self._repository.rollback()
            raise FotosMediaDeletionConflictError(media_id)

        keys = [locked.original_storage_key]
        keys.extend(
            item.storage_key for item in self._derivative_repository.list_by_media_id(media_id)
        )
        keys.extend(self._repository.reference_keys_for_media(media_id))
        root = self._settings.uploads_dir.resolve()
        scope = root / "fotos" / locked.organization_id / locked.tenant_id / locked.environment_id
        paths = []
        for key in keys:
            path = root / Path(key)
            if (
                not path.is_relative_to(scope)
                or not path.is_file()
                or path.is_symlink()
                or path.resolve() != path
            ):
                self._repository.rollback()
                raise FotosMediaFileNotFoundError(media_id)
            paths.append(path)
        if len(paths) != len(set(paths)):
            self._repository.rollback()
            raise FotosMediaStorageConflictError(media_id)

        stage = root / f".fotos-delete-{uuid4().hex}"
        moved: list[tuple[Path, Path]] = []
        committed = False
        try:
            stage.mkdir()
            for path in paths:
                target = stage / path.relative_to(root)
                target.parent.mkdir(parents=True, exist_ok=True)
                path.rename(target)
                moved.append((path, target))
            self._repository.delete_permanently(locked)
            committed = True
        finally:
            if not committed:
                self._repository.rollback()
                for path, target in reversed(moved):
                    path.parent.mkdir(parents=True, exist_ok=True)
                    target.rename(path)
                if stage.exists():
                    shutil.rmtree(stage)
        try:
            shutil.rmtree(stage)
        except OSError:
            logger.exception("Mídia excluída do banco, mas arquivos retidos em %s", stage)
            raise FotosMediaStorageMoveError(media_id) from None

    def _require_media(
        self,
        media_id: str,
    ) -> FotosMediaModel:
        """Retorna uma mídia ativa existente."""

        media = self._repository.find_by_id(
            media_id,
        )

        if media is None:
            raise FotosMediaNotFoundError(
                media_id,
            )

        return media

    def _require_media_for_update(
        self,
        media_id: str,
    ) -> FotosMediaModel:
        """Retorna e bloqueia uma mídia ativa para atualização."""

        media = self._repository.find_by_id_for_update(
            media_id,
        )

        if media is None:
            raise FotosMediaNotFoundError(
                media_id,
            )

        return media

    def _require_album(
        self,
        album_id: str,
    ) -> FotosAlbumModel:
        """Retorna um álbum existente."""

        album = self._album_repository.find_by_id(
            album_id,
        )

        if album is None:
            raise FotosMediaAlbumNotFoundError(
                album_id,
            )

        return album

    def _require_environment(
        self,
        environment_id: str,
    ) -> EnvironmentModel:
        """Retorna um ambiente existente."""

        environment = self._environment_repository.find_by_id(
            environment_id,
        )

        if environment is None:
            raise EnvironmentNotFoundError(
                environment_id,
            )

        return environment

    def _require_tenant(
        self,
        tenant_id: str,
    ) -> TenantModel:
        """Retorna um tenant existente."""

        tenant = self._tenant_repository.find_by_id(
            tenant_id,
        )

        if tenant is None:
            raise TenantNotFoundError(
                tenant_id,
            )

        return tenant

    def _require_album_matches_scope(
        self,
        album: FotosAlbumModel,
        *,
        organization_id: str | None,
        tenant_id: str | None,
        environment_id: str | None,
    ) -> None:
        """Valida se o álbum pertence ao escopo esperado."""

        if organization_id is not None and album.organization_id != organization_id:
            raise FotosMediaAlbumScopeMismatchError(
                album.id,
            )

        if tenant_id is not None and album.tenant_id != tenant_id:
            raise FotosMediaAlbumScopeMismatchError(
                album.id,
            )

        if environment_id is not None and album.environment_id != environment_id:
            raise FotosMediaAlbumScopeMismatchError(
                album.id,
            )

    @staticmethod
    def _normalize_datetime(
        value: datetime | None,
    ) -> datetime | None:
        """Normaliza uma data com timezone para UTC sem timezone."""

        if value is None or value.tzinfo is None:
            return value

        return value.astimezone(UTC).replace(tzinfo=None)


    def _require_roles(
        self,
        current_user: AuthenticatedUser,
        allowed_roles: frozenset[UserModuleRole],
    ) -> None:
        """Exige um papel funcional permitido no Deja Fotos."""

        self._authorization_service.require_module_roles(
            current_user,
            module_key=FOTOS_MODULE_KEY,
            allowed_roles=allowed_roles,
        )