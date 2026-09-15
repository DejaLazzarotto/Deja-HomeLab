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
from deja_indicadores_api.fotos.albums.models import (
    FotosAlbumModel,
)
from deja_indicadores_api.fotos.albums.repository import (
    FotosAlbumRepository,
)
from deja_indicadores_api.fotos.media.exceptions import (
    FotosMediaAlbumNotFoundError,
    FotosMediaAlbumScopeMismatchError,
    FotosMediaEmptyFileError,
    FotosMediaFileNotFoundError,
    FotosMediaInvalidContentError,
    FotosMediaInvalidTypeError,
    FotosMediaNotFoundError,
    FotosMediaTooLargeError,
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
    UserRole,
)

FOTOS_MEDIA_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)

FOTOS_MEDIA_OPERATOR_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
    }
)

FOTOS_MEDIA_MANAGER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
    }
)

ALLOWED_FOTOS_CONTENT_TYPES = {
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    "video/mp4": "video",
}

UPLOAD_CHUNK_SIZE = 1024 * 1024


class FotosMediaService:
    """Regras de aplicação das mídias do Deja Fotos."""

    def __init__(
        self,
        repository: FotosMediaRepository,
        album_repository: FotosAlbumRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
        settings: Settings,
    ) -> None:
        self._repository = repository
        self._album_repository = album_repository
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
        include_deleted: bool = False,
    ) -> list[FotosMediaModel]:
        """Lista mídias dentro do escopo permitido."""

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

        return self._repository.list(
            organization_id=effective_organization_id,
            tenant_id=effective_tenant_id,
            environment_id=effective_environment_id,
            album_id=album_id,
            media_type=media_type,
            processing_status=processing_status,
            include_deleted=include_deleted,
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

        content_type = (
            file.content_type
            or "application/octet-stream"
        )

        media_type = ALLOWED_FOTOS_CONTENT_TYPES.get(
            content_type
        )

        if media_type is None:
            raise FotosMediaInvalidTypeError(
                content_type,
            )

        original_name = Path(
            file.filename or "arquivo"
        ).name

        extension = Path(
            original_name
        ).suffix.lower()

        media_id = str(
            uuid4()
        )

        storage_key = (
            Path("fotos")
            / tenant.organization_id
            / tenant.id
            / environment.id
            / "originals"
            / media_id
            / f"original{extension}"
        )

        file_path = (
            self._settings.uploads_dir
            / storage_key
        )

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        max_size_bytes = (
            self._settings.fotos_media_max_size_mb
            * 1024
            * 1024
        )

        digest = sha256()
        total_size = 0

        width: int | None = None
        height: int | None = None
        duration_seconds: float | None = None
        original_date: datetime | None = None

        try:
            with file_path.open("wb") as destination:
                while True:
                    chunk = await file.read(
                        UPLOAD_CHUNK_SIZE
                    )

                    if not chunk:
                        break

                    total_size += len(chunk)

                    if total_size > max_size_bytes:
                        raise FotosMediaTooLargeError(
                            self._settings.fotos_media_max_size_mb,
                        )

                    digest.update(
                        chunk
                    )
                    destination.write(
                        chunk
                    )

            if total_size == 0:
                raise FotosMediaEmptyFileError()

            if media_type == "image":
                try:
                    inspection = inspect_image(
                        file_path,
                    )
                except FotosImageInspectionError as exc:
                    raise FotosMediaInvalidContentError(
                        str(exc),
                    ) from exc

                width = inspection.width
                height = inspection.height
                original_date = inspection.original_date

            elif media_type == "video":
                try:
                    inspection = inspect_video(
                        file_path,
                        ffprobe_executable=(
                            self._settings.ffprobe_executable
                        ),
                    )
                except FotosVideoInspectionError as exc:
                    raise FotosMediaInvalidContentError(
                        str(exc),
                    ) from exc

                width = inspection.width
                height = inspection.height
                duration_seconds = inspection.duration_seconds

        except Exception:
            if file_path.exists():
                file_path.unlink()

            raise

        media = FotosMediaModel(
            id=media_id,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
            album_id=album_id,
            original_name=original_name,
            media_type=media_type,
            content_type=content_type,
            file_extension=extension or None,
            file_size=total_size,
            checksum_sha256=digest.hexdigest(),
            original_storage_key=storage_key.as_posix(),
            processing_status="received",
            processing_error=None,
            original_date=original_date,
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

        file_path = (
            self._settings.uploads_dir
            / Path(media.original_storage_key)
        )

        if (
            not file_path.exists()
            or not file_path.is_file()
        ):
            raise FotosMediaFileNotFoundError(
                media.id,
            )

        return file_path, media

    def delete(
        self,
        media_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        """Realiza exclusão lógica de uma mídia."""

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

        media.deleted_at = datetime.now(
            UTC
        ).replace(
            tzinfo=None
        )

        self._repository.update(
            media,
        )

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

        environment = (
            self._environment_repository.find_by_id(
                environment_id,
            )
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

        if (
            organization_id is not None
            and album.organization_id != organization_id
        ):
            raise FotosMediaAlbumScopeMismatchError(
                album.id,
            )

        if (
            tenant_id is not None
            and album.tenant_id != tenant_id
        ):
            raise FotosMediaAlbumScopeMismatchError(
                album.id,
            )

        if (
            environment_id is not None
            and album.environment_id != environment_id
        ):
            raise FotosMediaAlbumScopeMismatchError(
                album.id,
            )

    def _require_roles(
        self,
        current_user: AuthenticatedUser,
        allowed_roles: frozenset[UserRole],
    ) -> None:
        """Exige um papel permitido para a operação."""

        self._authorization_service.require_roles(
            current_user,
            allowed_roles,
        )