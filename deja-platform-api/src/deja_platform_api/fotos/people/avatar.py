"""Upload e leitura do avatar de uma pessoa."""

import logging
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps

from deja_platform_api.authentication.authorization import (
    AuthorizationService,
)
from deja_platform_api.authentication.schemas import (
    AuthenticatedUser,
)
from deja_platform_api.core.config import Settings
from deja_platform_api.fotos.media.derivative_service import (
    FotosMediaDerivativeService,
)
from deja_platform_api.fotos.media.service import FotosMediaService
from deja_platform_api.fotos.people.exceptions import (
    FotosPersonAvatarInvalidError,
    FotosPersonAvatarNotFoundError,
    FotosPersonAvatarTooLargeError,
)
from deja_platform_api.fotos.people.models import FotosPersonModel
from deja_platform_api.fotos.people.repository import (
    FotosPersonRepository,
)
from deja_platform_api.fotos.people.service import (
    FOTOS_MODULE_KEY,
    PERSON_EDITOR_ROLES,
    FotosPersonService,
)
from deja_platform_api.fotos.people.storage import (
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
        media_service: FotosMediaService,
        derivative_service: FotosMediaDerivativeService,
    ) -> None:
        self._person_service = person_service
        self._repository = repository
        self._authorization_service = authorization_service
        self._settings = settings
        self._media_service = media_service
        self._derivative_service = derivative_service

    def list_avatar_faces(
        self,
        person_id: str,
        current_user: AuthenticatedUser,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list, int]:
        """Lista rostos confirmados de uma pessoa autorizada."""

        person = self._person_service.find_by_id(
            person_id,
            current_user,
        )

        return self._repository.list_confirmed_faces_for_person(
            person,
            page=page,
            page_size=page_size,
        )

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

    def get_face_avatar_preview(
        self,
        person_id: str,
        face_id: str,
        current_user: AuthenticatedUser,
    ) -> bytes:
        """Retorna o recorte de um rosto confirmado sem salvar avatar."""
        person = self._person_service.find_by_id(
            person_id,
            current_user,
        )

        face = self._repository.get_confirmed_face_for_person(
            person,
            face_id,
        )

        if face is None:
            raise FotosPersonAvatarInvalidError()

        self._media_service.find_by_id(
            face.media_id,
            current_user,
        )

        preview_path, _ = self._derivative_service.get_derivative_file(
            face.media_id,
            "preview",
        )

        if preview_path.stat().st_size > MAX_AVATAR_SIZE_BYTES:
            raise FotosPersonAvatarTooLargeError()

        return self._crop_face(
            preview_path.read_bytes(),
            face.x,
            face.y,
            face.width,
            face.height,
        )
    def use_face_as_avatar(
        self,
        person_id: str,
        face_id: str,
        current_user: AuthenticatedUser,
    ) -> FotosPersonModel:
        """Define como avatar o recorte de um rosto confirmado."""
        self._authorization_service.require_module_roles(
            current_user,
            module_key=FOTOS_MODULE_KEY,
            allowed_roles=PERSON_EDITOR_ROLES,
        )

        content = self.get_face_avatar_preview(
            person_id,
            face_id,
            current_user,
        )

        person = self._person_service.find_by_id(
            person_id,
            current_user,
        )

        return self._save_avatar(person, content)

    def _save_avatar(
        self,
        person: FotosPersonModel,
        content: bytes,
    ) -> FotosPersonModel:
        """Grava avatar normalizado preservando a versão anterior em caso de erro."""
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
        previous_content_type = person.avatar_content_type
        previous_file_size = person.avatar_file_size
        previous_checksum = person.avatar_checksum_sha256

        person.avatar_storage_key = storage_key.as_posix()
        person.avatar_content_type = "image/webp"
        person.avatar_file_size = len(content)
        person.avatar_checksum_sha256 = sha256(
            content
        ).hexdigest()

        try:
            updated = self._repository.update(person)
        except Exception:
            person.avatar_storage_key = previous_key
            person.avatar_content_type = previous_content_type
            person.avatar_file_size = previous_file_size
            person.avatar_checksum_sha256 = previous_checksum
            path.unlink(missing_ok=True)
            raise

        self._remove_previous(previous_key)
        return updated

    def remove(
        self,
        person_id: str,
        current_user: AuthenticatedUser,
    ) -> FotosPersonModel:
        self._authorization_service.require_module_roles(
            current_user,
            module_key=FOTOS_MODULE_KEY,
            allowed_roles=PERSON_EDITOR_ROLES,
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
    def _crop_face(
        source: bytes,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> bytes:
        """Recorta um rosto em coordenadas normalizadas e gera WebP quadrado."""
        from math import isfinite

        coordinates = (x, y, width, height)
        if (
            not all(isfinite(value) for value in coordinates)
            or x < 0
            or y < 0
            or width <= 0
            or height <= 0
            or x + width > 1.000001
            or y + height > 1.000001
        ):
            raise FotosPersonAvatarInvalidError()

        try:
            with Image.open(BytesIO(source)) as original:
                if (
                    original.format not in ALLOWED_AVATAR_FORMATS
                    or original.width * original.height > MAX_AVATAR_PIXELS
                ):
                    raise FotosPersonAvatarInvalidError()

                image = ImageOps.exif_transpose(original)
                image = image.convert("RGB")

                face_x = (x + width / 2) * image.width
                face_y = (y + height / 2) * image.height

                side = max(
                    width * image.width,
                    height * image.height,
                ) * 1.8
                side = min(
                    side,
                    image.width,
                    image.height,
                )

                center_x = max(
                    side / 2,
                    min(face_x, image.width - side / 2),
                )
                center_y = max(
                    side / 2,
                    min(face_y, image.height - side / 2),
                )

                box = (
                    round(center_x - side / 2),
                    round(center_y - side / 2),
                    round(center_x + side / 2),
                    round(center_y + side / 2),
                )

                cropped = image.crop(box)
                cropped = cropped.resize(
                    AVATAR_SIZE,
                    Image.Resampling.LANCZOS,
                )

                output = BytesIO()
                cropped.save(output, format="WEBP", quality=85)
                return output.getvalue()
        except (OSError, ValueError, Image.DecompressionBombError) as exc:
            raise FotosPersonAvatarInvalidError() from exc
