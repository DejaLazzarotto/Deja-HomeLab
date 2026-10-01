"""Revisão de rostos e ensino de referências com isolamento institucional."""

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps
from sqlalchemy import exists, extract, func, or_, select
from sqlalchemy.orm import Session

from deja_indicadores_api.authentication.authorization import AuthorizationService
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.core.config import Settings
from deja_indicadores_api.core.exceptions import (
    ApplicationError,
    ResourceConflictError,
    ResourceNotFoundError,
)
from deja_indicadores_api.fotos.curation import engine
from deja_indicadores_api.fotos.curation.models import FotosFaceModel, FotosFaceReferenceModel
from deja_indicadores_api.fotos.curation.repository import FotosFaceRepository
from deja_indicadores_api.fotos.curation.schemas import FaceCreate
from deja_indicadores_api.fotos.media.derivative_service import FotosMediaDerivativeService
from deja_indicadores_api.fotos.media.models import FotosMediaModel
from deja_indicadores_api.fotos.media.service import FotosMediaService
from deja_indicadores_api.fotos.people.models import FotosPersonMediaModel, FotosPersonModel
from deja_indicadores_api.fotos.people.service import (
    FOTOS_MODULE_KEY,
    PERSON_MANAGER_ROLES,
    FotosPersonService,
)


class FaceNotFound(ResourceNotFoundError):
    error_code = "fotos_face_not_found"


class FaceInvalid(ResourceConflictError):
    error_code = "fotos_face_invalid"


class FaceEngineError(ApplicationError):
    error_code = "fotos_face_engine_unavailable"
    status_code = 503


def crop_face(path: Path, face: FotosFaceModel) -> Image.Image:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        w, h = image.size
        box = (
            round(face.x * w),
            round(face.y * h),
            round((face.x + face.width) * w),
            round((face.y + face.height) * h),
        )
        if box[2] - box[0] < 32 or box[3] - box[1] < 32:
            raise FaceInvalid("O rosto deve ter pelo menos 32 pixels em cada dimensão.")
        return image.crop(box)


def same_face_box(face: FotosFaceModel, box: tuple[float, float, float, float]) -> bool:
    x, y, width, height = box
    intersection = max(0.0, min(face.x + face.width, x + width) - max(face.x, x)) * max(
        0.0, min(face.y + face.height, y + height) - max(face.y, y)
    )
    smaller_area = min(face.width * face.height, width * height)
    return smaller_area > 0 and intersection / smaller_area >= 0.60


class FotosCurationService:
    def __init__(
        self,
        repository: FotosFaceRepository,
        session: Session,
        media_service: FotosMediaService,
        person_service: FotosPersonService,
        derivatives: FotosMediaDerivativeService,
        settings: Settings,
    ) -> None:
        self.repo = repository
        self.session = session
        self.media_service = media_service
        self.person_service = person_service
        self.derivatives = derivatives
        self.settings = settings
        self.authorization = AuthorizationService()

    def _manager(self, user: AuthenticatedUser) -> None:
        self.authorization.require_module_roles(
        user,
        module_key=FOTOS_MODULE_KEY,
        allowed_roles=PERSON_MANAGER_ROLES,
    )

    def _media(self, media_id: str, user: AuthenticatedUser) -> FotosMediaModel:
        return self.media_service.find_by_id(media_id, user)

    def _person(
        self, person_id: str, media: FotosMediaModel, user: AuthenticatedUser
    ) -> FotosPersonModel:
        person = self.person_service.find_by_id(person_id, user)
        if (person.organization_id, person.tenant_id, person.environment_id) != (
            media.organization_id,
            media.tenant_id,
            media.environment_id,
        ) or not person.active:
            raise FaceInvalid("A pessoa ativa deve pertencer ao ambiente da mídia.")
        return person

    def _face(
        self, face_id: str, user: AuthenticatedUser
    ) -> tuple[FotosFaceModel, FotosMediaModel]:
        face = self.repo.get(face_id)
        if face is None:
            raise FaceNotFound("Rosto não encontrado.")
        media = self._media(face.media_id, user)
        if (face.organization_id, face.tenant_id, face.environment_id) != (
            media.organization_id,
            media.tenant_id,
            media.environment_id,
        ):
            raise FaceNotFound("Rosto não encontrado.")
        return face, media

    def _require_image_media(self, media: FotosMediaModel) -> None:
        if media.media_type != "image":
            raise FaceInvalid("A curadoria facial é suportada apenas para fotos.")

    def _image(self, media: FotosMediaModel) -> Path:
        kind = "poster" if media.media_type == "video" else "preview"
        path, _ = self.derivatives.get_derivative_file(media.id, kind)
        return path

    def list_faces(
        self, media_id: str, user: AuthenticatedUser, *, page: int, page_size: int
    ) -> tuple[list[FotosFaceModel], int]:
        media = self._media(media_id, user)
        return self.repo.list_faces(media.id, media.environment_id, page=page, page_size=page_size)

    def list_media(
        self,
        user: AuthenticatedUser,
        *,
        environment_id: str | None,
        album_id: str | None,
        person_id: str | None,
        situation: str,
        year: int | None,
        month: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[FotosMediaModel], int]:
        org, tenant, environment = self.authorization.resolve_list_scope(
            user, organization_id=None, tenant_id=None, environment_id=environment_id
        )
        where = [
            FotosMediaModel.deleted_at.is_(None),
            FotosMediaModel.processing_status == "ready",
        ]
        if org:
            where.append(FotosMediaModel.organization_id == org)
        if tenant:
            where.append(FotosMediaModel.tenant_id == tenant)
        if environment:
            where.append(FotosMediaModel.environment_id == environment)
        if album_id:
            where.append(FotosMediaModel.album_id == album_id)
        if year:
            where.append(extract("year", FotosMediaModel.original_date) == year)
        if month:
            where.append(extract("month", FotosMediaModel.original_date) == month)
        if situation != "all":
            where.append(
                exists(
                    select(FotosFaceModel.id).where(
                        FotosFaceModel.media_id == FotosMediaModel.id,
                        FotosFaceModel.status.in_(
                            ("unknown", "rejected") if situation == "unknown" else (situation,)
                        ),
                    )
                )
            )
        if person_id:
            where.append(
                or_(
                    exists(
                        select(FotosFaceModel.id).where(
                            FotosFaceModel.media_id == FotosMediaModel.id,
                            FotosFaceModel.person_id == person_id,
                        )
                    ),
                    exists(
                        select(FotosPersonMediaModel.person_id).where(
                            FotosPersonMediaModel.media_id == FotosMediaModel.id,
                            FotosPersonMediaModel.person_id == person_id,
                            FotosPersonMediaModel.environment_id == FotosMediaModel.environment_id,
                            FotosPersonMediaModel.organization_id
                            == FotosMediaModel.organization_id,
                            FotosPersonMediaModel.tenant_id == FotosMediaModel.tenant_id,
                        )
                    ),
                )
            )
        total = int(self.session.scalar(select(func.count(FotosMediaModel.id)).where(*where)) or 0)
        items = self.session.scalars(
            select(FotosMediaModel)
            .where(*where)
            .order_by(FotosMediaModel.original_date.desc(), FotosMediaModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return list(items), total

    def summary(self, user: AuthenticatedUser, environment_id: str | None) -> dict[str, int]:
        org, tenant, environment = self.authorization.resolve_list_scope(
            user, organization_id=None, tenant_id=None, environment_id=environment_id
        )
        conditions = [
            FotosMediaModel.deleted_at.is_(None),
            FotosFaceModel.media_id == FotosMediaModel.id,
        ]
        if org:
            conditions.append(FotosMediaModel.organization_id == org)
        if tenant:
            conditions.append(FotosMediaModel.tenant_id == tenant)
        if environment:
            conditions.append(FotosMediaModel.environment_id == environment)
        result = {}
        for name, statuses in (("pending", ("suggested",)), ("unknown", ("unknown", "rejected"))):
            result[name] = int(
                self.session.scalar(
                    select(func.count(FotosFaceModel.id))
                    .select_from(FotosFaceModel)
                    .join(FotosMediaModel, FotosFaceModel.media_id == FotosMediaModel.id)
                    .where(*conditions, FotosFaceModel.status.in_(statuses))
                )
                or 0
            )
        return result

    def create(self, media_id: str, data: FaceCreate, user: AuthenticatedUser) -> FotosFaceModel:
        self._manager(user)
        media = self._media(media_id, user)
        if media.processing_status != "ready":
            raise FaceInvalid("A mídia precisa estar pronta para marcação.")
        self._require_image_media(media)
        self._image(media)
        if data.person_id:
            self._person(data.person_id, media, user)
        face = FotosFaceModel(
            id=str(uuid4()),
            media_id=media.id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            x=data.x,
            y=data.y,
            width=data.width,
            height=data.height,
            origin="manual",
            status="confirmed" if data.person_id else "unknown",
            person_id=data.person_id,
        )
        self.repo.add(face)
        if data.person_id:
            self._ensure_link(data.person_id, media)
        return face

    def confirm(
        self, face_id: str, person_id: str | None, user: AuthenticatedUser
    ) -> FotosFaceModel:
        self._manager(user)
        face, media = self._face(face_id, user)
        chosen = person_id or (face.person_id if face.status == "suggested" else None)
        if not chosen:
            raise FaceInvalid("Escolha uma pessoa para confirmar o rosto.")
        self._person(chosen, media, user)
        reference = self.repo.reference_for_face(face.id)
        if reference and reference.person_id != chosen:
            raise FaceInvalid("Remova a referência facial antes de mudar a pessoa.")
        face.person_id = chosen
        face.rejected_person_id = None
        face.status = "confirmed"
        self.repo.save()
        self._ensure_link(chosen, media)
        return face

    def reject(self, face_id: str, user: AuthenticatedUser) -> FotosFaceModel:
        self._manager(user)
        face, _ = self._face(face_id, user)
        if face.status != "suggested":
            raise FaceInvalid("Somente sugestões pendentes podem ser rejeitadas.")
        face.rejected_person_id = face.person_id
        face.person_id = None
        face.status = "rejected"
        self.repo.save()
        return face

    def delete(self, face_id: str, user: AuthenticatedUser) -> None:
        self._manager(user)
        face, _ = self._face(face_id, user)
        reference = self.repo.reference_for_face(face.id)
        if reference:
            self.remove_reference(reference.id, user)
        # Vínculos manuais preexistentes permanecem intactos.
        self.repo.delete(face)

    def _ensure_link(self, person_id: str, media: FotosMediaModel) -> None:
        if self.session.get(FotosPersonMediaModel, (person_id, media.id)):
            return
        self.session.add(
            FotosPersonMediaModel(
                person_id=person_id,
                media_id=media.id,
                organization_id=media.organization_id,
                tenant_id=media.tenant_id,
                environment_id=media.environment_id,
            )
        )
        self.session.commit()

    def list_references(
        self, person_id: str, user: AuthenticatedUser, *, page: int, page_size: int
    ) -> tuple[list[FotosFaceReferenceModel], int]:
        person = self.person_service.find_by_id(person_id, user)
        return self.repo.list_references(
            person.environment_id, person_id=person.id, page=page, page_size=page_size
        )

    def teach(self, face_id: str, user: AuthenticatedUser) -> FotosFaceReferenceModel:
        self._manager(user)
        face, media = self._face(face_id, user)
        self._require_image_media(media)
        if face.status != "confirmed" or not face.person_id:
            raise FaceInvalid("Confirme a pessoa antes de ensinar a IA.")
        existing = self.repo.reference_for_face(face.id)
        if existing:
            return existing
        self._person(face.person_id, media, user)
        crop = crop_face(self._image(media), face)
        try:
            from PIL import ImageStat

            if ImageStat.Stat(crop.convert("L")).stddev[0] < 12:
                raise FaceInvalid("Rosto desfocado ou sem detalhes; mantenha a marcação manual.")
            if not engine.validate_reference(crop, self.settings.fotos_face_models_dir):
                raise FaceInvalid("Não foi encontrado um rosto no recorte; ajuste a marcação.")
        except engine.FaceEngineUnavailable as exc:
            raise FaceEngineError(str(exc)) from exc
        crop.thumbnail((320, 320))
        output = BytesIO()
        crop.save(output, format="WEBP", quality=90)
        key = (
            Path("fotos")
            / media.organization_id
            / media.tenant_id
            / media.environment_id
            / "face-references"
            / face.person_id
            / f"{face.id}.webp"
        )
        path = self.settings.uploads_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(output.getvalue())
        reference = FotosFaceReferenceModel(
            id=str(uuid4()),
            face_id=face.id,
            person_id=face.person_id,
            organization_id=media.organization_id,
            tenant_id=media.tenant_id,
            environment_id=media.environment_id,
            storage_key=key.as_posix(),
        )
        try:
            self.repo.add(reference)
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return reference

    def reference_file(self, reference_id: str, user: AuthenticatedUser) -> Path:
        reference = self.session.get(FotosFaceReferenceModel, reference_id)
        if not reference:
            raise FaceNotFound("Referência não encontrada.")
        person = self.person_service.find_by_id(reference.person_id, user)
        if (reference.organization_id, reference.tenant_id, reference.environment_id) != (
            person.organization_id,
            person.tenant_id,
            person.environment_id,
        ):
            raise FaceNotFound("Referência não encontrada.")
        path = self.settings.uploads_dir / reference.storage_key
        if not path.is_file():
            raise FaceNotFound("Arquivo de referência não encontrado.")
        return path

    def remove_reference(self, reference_id: str, user: AuthenticatedUser) -> None:
        self._manager(user)
        path = self.reference_file(reference_id, user)
        reference = self.session.get(FotosFaceReferenceModel, reference_id)
        self.repo.delete(reference)
        path.unlink(missing_ok=True)

    def detect(self, media_id: str, user: AuthenticatedUser) -> list[FotosFaceModel]:
        self._manager(user)
        media = self._media(media_id, user)
        if media.processing_status != "ready":
            raise FaceInvalid("A mídia precisa estar pronta para análise.")
        self._require_image_media(media)
        path = self._image(media)
        try:
            boxes = engine.detect(path, self.settings.fotos_face_models_dir)
        except engine.FaceEngineUnavailable as exc:
            raise FaceEngineError(str(exc)) from exc
        existing = self.repo.all_for_media(media.id, media.environment_id)
        references = [
            (ref.person_id, self.settings.uploads_dir / ref.storage_key)
            for ref in self.repo.all_references(media.environment_id)
        ]
        updated = []
        if references:
            for face in existing:
                if face.status != "unknown":
                    continue
                try:
                    crop = crop_face(path, face)
                except FaceInvalid:
                    continue
                try:
                    match = engine.suggest(crop, references, self.settings.fotos_face_models_dir)
                    if not match:
                        match = engine.suggest_in_image(
                            path,
                            (face.x, face.y, face.width, face.height),
                            references,
                            self.settings.fotos_face_models_dir,
                        )
                except engine.FaceEngineUnavailable as exc:
                    raise FaceEngineError(str(exc)) from exc
                if match:
                    face.person_id, face.confidence = match
                    face.status = "suggested"
                    updated.append(face)
            if updated:
                self.repo.save()
        created = []
        for x, y, width, height in boxes:
            if any(same_face_box(face, (x, y, width, height)) for face in existing):
                continue
            face = FotosFaceModel(
                id=str(uuid4()),
                media_id=media.id,
                organization_id=media.organization_id,
                tenant_id=media.tenant_id,
                environment_id=media.environment_id,
                x=x,
                y=y,
                width=width,
                height=height,
                origin="detected",
                status="unknown",
            )
            try:
                match = engine.suggest(
                    crop_face(path, face), references, self.settings.fotos_face_models_dir
                )
                if not match:
                    match = engine.suggest_in_image(
                        path,
                        (x, y, width, height),
                        references,
                        self.settings.fotos_face_models_dir,
                    )
            except engine.FaceEngineUnavailable as exc:
                raise FaceEngineError(str(exc)) from exc
            if match:
                person_id, confidence = match
                face.person_id = person_id
                face.confidence = confidence
                face.status = "suggested"
            self.repo.add(face)
            created.append(face)
            existing.append(face)
        return [*updated, *created]
