"""Upload e leitura do avatar de uma pessoa."""

import logging
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.fotos.people.exceptions import (
    FotosPersonAvatarInvalidError,
    FotosPersonAvatarNotFoundError,
    FotosPersonAvatarTooLargeError,
)
from deja_indicadores_api.fotos.people.models import FotosPersonModel
from deja_indicadores_api.fotos.people.repository import (
    FotosPersonRepository,
)
from deja_indicadores_api.fotos.people.service import (
    PERSON_EDITOR_ROLES,
    FotosPersonService,
)
from deja_indicadores_api.fotos.people.storage import (
    build_avatar_storage_key,
    resolve_avatar_file,
)

logger = logging.getLogger(__name__)

MAX_AVATAR_SIZE_BYTES = 10 * 1024 * 1024
MAX_AVATAR_PIXELS = 40_000_000
AVATAR_SIZE = (512, 512)
ALLOWED_AVATAR_FORMATS = frozenset(
    {"JPEG", "PNG", "WEBP"}
)


class FotosPersonAvatarService:
    """Mantém avatar independente de fotos e assinaturas faciais."""

    def __init__(
        self,
        person_service: FotosPersonService,
        repository: FotosPersonRepository,
        authorization_service: AuthorizationService,
        settings: Settings,
    ) -> None:
        self._person_service = person_service
        self._repository = repository
        self._authorization_service = authorization_service
        self._settings = settings

    def get_file(
        self,
        person_id: str,
        current_user: AuthenticatedUser,
    ) -> Path:
        person = self._person_service.find_by_id(
            person_id,
            current_user,
        )
        if person.avatar_storage_key is None:
            raise FotosPersonAvatarNotFoundError()

        try:
            path = resolve_avatar_file(
                self._settings.uploads_dir,
                person.avatar_storage_key,
            )
        except ValueError as exc:
            raise FotosPersonAvatarNotFoundError() from exc

        if not path.is_file():
            raise FotosPersonAvatarNotFoundError()

        return path

    async def upload(
        self,
        person_id: str,
        file: UploadFile,
        current_user: AuthenticatedUser,
    ) -> FotosPersonModel:
        self._authorization_service.require_roles(
            current_user,
            PERSON_EDITOR_ROLES,
        )
        person = self._person_service.find_by_id(
            person_id,
            current_user,
        )

        source = await file.read(MAX_AVATAR_SIZE_BYTES + 1)
        if len(source) > MAX_AVATAR_SIZE_BYTES:
            raise FotosPersonAvatarTooLargeError()
        if not source:
            raise FotosPersonAvatarInvalidError()

        content = self._normalize(source)
        storage_key = build_avatar_storage_key(
            organization_id=person.organization_id,
            tenant_id=person.tenant_id,
            environment_id=person.environment_id,
            person_id=person.id,
            avatar_id=str(uuid4()),
        )
        path = resolve_avatar_file(
            self._settings.uploads_dir,
            storage_key.as_posix(),
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

        previous_key = person.avatar_storage_key
        person.avatar_storage_key = storage_key.as_posix()
        person.avatar_content_type = "image/webp"
        person.avatar_file_size = len(content)
        person.avatar_checksum_sha256 = sha256(
            content
        ).hexdigest()

        try:
            updated = self._repository.update(person)
        except Exception:
            path.unlink(missing_ok=True)
            raise

        self._remove_previous(previous_key)
        return updated

    def remove(
        self,
        person_id: str,
        current_user: AuthenticatedUser,
    ) -> FotosPersonModel:
        self._authorization_service.require_roles(
            current_user,
            PERSON_EDITOR_ROLES,
        )
        person = self._person_service.find_by_id(
            person_id,
            current_user,
        )

        previous_key = person.avatar_storage_key
        person.avatar_storage_key = None
        person.avatar_content_type = None
        person.avatar_file_size = None
        person.avatar_checksum_sha256 = None

        updated = self._repository.update(person)
        self._remove_previous(previous_key)
        return updated

    def delete_person(
        self,
        person_id: str,
        current_user: AuthenticatedUser,
    ) -> None:
        person = self._person_service.find_by_id(person_id, current_user)
        previous_key = person.avatar_storage_key
        reference_keys = self._repository.reference_keys_for_person(person_id)
        self._person_service.delete(person_id, current_user)
        self._remove_previous(previous_key)
        for key in reference_keys:
            self._remove_previous(key)

    def _remove_previous(
        self,
        storage_key: str | None,
    ) -> None:
        if storage_key is None:
            return

        try:
            path = resolve_avatar_file(
                self._settings.uploads_dir,
                storage_key,
            )
            path.unlink(missing_ok=True)
        except (OSError, ValueError):
            logger.warning(
                "Não foi possível remover um avatar anterior.",
                exc_info=True,
            )

    @staticmethod
    def _normalize(source: bytes) -> bytes:
        try:
            with Image.open(BytesIO(source)) as image:
                if (
                    image.format not in ALLOWED_AVATAR_FORMATS
                    or image.width * image.height
                    > MAX_AVATAR_PIXELS
                ):
                    raise FotosPersonAvatarInvalidError()

                normalized = ImageOps.exif_transpose(image)
                has_alpha = (
                    normalized.mode in ("RGBA", "LA")
                    or "transparency" in normalized.info
                )
                normalized = normalized.convert(
                    "RGBA" if has_alpha else "RGB"
                )
                normalized.thumbnail(AVATAR_SIZE)

                output = BytesIO()
                normalized.save(
                    output,
                    format="WEBP",
                    quality=85,
                )
                return output.getvalue()
        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            Image.DecompressionBombError,
        ) as exc:
            raise FotosPersonAvatarInvalidError() from exc
