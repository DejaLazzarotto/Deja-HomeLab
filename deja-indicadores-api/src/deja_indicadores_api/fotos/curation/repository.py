"""Consultas paginadas de rostos e referências."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.curation.models import FotosFaceModel, FotosFaceReferenceModel
from deja_indicadores_api.fotos.people.models import FotosPersonModel


class FotosFaceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, face_id: str) -> FotosFaceModel | None:
        return self.session.get(FotosFaceModel, face_id)

    def list_faces(
        self, media_id: str, environment_id: str, *, page: int, page_size: int
    ) -> tuple[list[FotosFaceModel], int]:
        where = (
            FotosFaceModel.media_id == media_id,
            FotosFaceModel.environment_id == environment_id,
        )
        total = self.session.scalar(select(func.count(FotosFaceModel.id)).where(*where)) or 0
        items = self.session.scalars(
            select(FotosFaceModel)
            .where(*where)
            .order_by(FotosFaceModel.created_at, FotosFaceModel.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return list(items), total

    def all_for_media(self, media_id: str, environment_id: str) -> list[FotosFaceModel]:
        return list(
            self.session.scalars(
                select(FotosFaceModel).where(
                    FotosFaceModel.media_id == media_id,
                    FotosFaceModel.environment_id == environment_id,
                )
            ).all()
        )

    def list_references(
        self,
        environment_id: str,
        *,
        person_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[FotosFaceReferenceModel], int]:
        where = [FotosFaceReferenceModel.environment_id == environment_id]
        if person_id:
            where.append(FotosFaceReferenceModel.person_id == person_id)
        total = (
            self.session.scalar(select(func.count(FotosFaceReferenceModel.id)).where(*where)) or 0
        )
        items = self.session.scalars(
            select(FotosFaceReferenceModel)
            .where(*where)
            .order_by(FotosFaceReferenceModel.created_at, FotosFaceReferenceModel.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return list(items), total

    def all_references(self, environment_id: str) -> list[FotosFaceReferenceModel]:
        return list(
            self.session.scalars(
                select(FotosFaceReferenceModel)
                .join(FotosPersonModel, FotosFaceReferenceModel.person_id == FotosPersonModel.id)
                .where(
                    FotosFaceReferenceModel.environment_id == environment_id,
                    FotosPersonModel.environment_id == environment_id,
                    FotosPersonModel.organization_id == FotosFaceReferenceModel.organization_id,
                    FotosPersonModel.tenant_id == FotosFaceReferenceModel.tenant_id,
                    FotosPersonModel.active.is_(True),
                )
                .order_by(FotosFaceReferenceModel.id)
            ).all()
        )

    def reference_for_face(self, face_id: str) -> FotosFaceReferenceModel | None:
        return self.session.scalar(
            select(FotosFaceReferenceModel).where(FotosFaceReferenceModel.face_id == face_id)
        )

    def add(self, item: FotosFaceModel | FotosFaceReferenceModel) -> None:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)

    def save(self) -> None:
        self.session.commit()

    def delete(self, item: FotosFaceModel | FotosFaceReferenceModel) -> None:
        self.session.delete(item)
        self.session.commit()
