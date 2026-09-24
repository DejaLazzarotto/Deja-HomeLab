"""Persistência de pessoas e seus vínculos com mídias."""

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.curation.models import FotosFaceModel, FotosFaceReferenceModel
from deja_indicadores_api.fotos.media.models import (
    FotosMediaModel,
)
from deja_indicadores_api.fotos.people.models import (
    FotosPersonMediaModel,
    FotosPersonModel,
)


class FotosPersonRepository:
    """Consultas e alterações de Pessoas do Deja Fotos."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[FotosPersonModel], int]:
        conditions = []

        if organization_id is not None:
            conditions.append(FotosPersonModel.organization_id == organization_id)
        if tenant_id is not None:
            conditions.append(FotosPersonModel.tenant_id == tenant_id)
        if environment_id is not None:
            conditions.append(FotosPersonModel.environment_id == environment_id)
        if active is not None:
            conditions.append(FotosPersonModel.active == active)
        if name:
            conditions.append(FotosPersonModel.name.ilike(f"%{name}%"))

        total = int(
            self._session.scalar(select(func.count(FotosPersonModel.id)).where(*conditions)) or 0
        )

        statement = (
            select(FotosPersonModel)
            .where(*conditions)
            .order_by(
                FotosPersonModel.name,
                FotosPersonModel.id,
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(self._session.scalars(statement).all()), total

    def find_by_id(
        self,
        person_id: str,
    ) -> FotosPersonModel | None:
        return self._session.get(FotosPersonModel, person_id)

    def find_by_scope_and_name(
        self,
        *,
        organization_id: str,
        tenant_id: str,
        environment_id: str,
        name: str,
    ) -> FotosPersonModel | None:
        statement = select(FotosPersonModel).where(
            FotosPersonModel.organization_id == organization_id,
            FotosPersonModel.tenant_id == tenant_id,
            FotosPersonModel.environment_id == environment_id,
            FotosPersonModel.name == name,
        )

        return self._session.scalar(statement)

    def add(
        self,
        person: FotosPersonModel,
    ) -> FotosPersonModel:
        self._session.add(person)
        self._session.commit()
        self._session.refresh(person)
        return person

    def update(
        self,
        person: FotosPersonModel,
    ) -> FotosPersonModel:
        self._session.commit()
        self._session.refresh(person)
        return person

    def delete(self, person: FotosPersonModel) -> None:
        self._session.delete(person)
        self._session.commit()

    def list_media(
        self,
        person: FotosPersonModel,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[FotosMediaModel], int]:
        conditions = (
            FotosPersonMediaModel.person_id == person.id,
            FotosPersonMediaModel.organization_id == person.organization_id,
            FotosPersonMediaModel.tenant_id == person.tenant_id,
            FotosPersonMediaModel.environment_id == person.environment_id,
            FotosMediaModel.organization_id == person.organization_id,
            FotosMediaModel.tenant_id == person.tenant_id,
            FotosMediaModel.environment_id == person.environment_id,
            FotosMediaModel.deleted_at.is_(None),
        )

        total = int(
            self._session.scalar(
                select(func.count(FotosMediaModel.id))
                .join(
                    FotosPersonMediaModel,
                    FotosPersonMediaModel.media_id == FotosMediaModel.id,
                )
                .where(*conditions)
            )
            or 0
        )

        statement = (
            select(FotosMediaModel)
            .join(
                FotosPersonMediaModel,
                FotosPersonMediaModel.media_id == FotosMediaModel.id,
            )
            .where(*conditions)
            .order_by(
                FotosMediaModel.original_date.desc(),
                FotosMediaModel.created_at.desc(),
                FotosMediaModel.id.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(self._session.scalars(statement).all()), total

    def find_link(
        self,
        person_id: str,
        media_id: str,
    ) -> FotosPersonMediaModel | None:
        return self._session.get(
            FotosPersonMediaModel,
            (person_id, media_id),
        )

    def add_link(
        self,
        link: FotosPersonMediaModel,
    ) -> None:
        self._session.add(link)
        self._session.commit()

    def delete_link(
        self,
        link: FotosPersonMediaModel,
    ) -> None:
        self._session.delete(link)
        self._session.commit()

    def has_confirmed_face(self, person_id: str, media_id: str) -> bool:
        return (
            self._session.scalar(
                select(FotosFaceModel.id)
                .where(
                    FotosFaceModel.person_id == person_id,
                    FotosFaceModel.media_id == media_id,
                    FotosFaceModel.status == "confirmed",
                )
                .limit(1)
            )
            is not None
        )

    def reference_keys_for_person(self, person_id: str) -> list[str]:
        return list(
            self._session.scalars(
                select(FotosFaceReferenceModel.storage_key).where(
                    FotosFaceReferenceModel.person_id == person_id
                )
            ).all()
        )

    def clear_faces_for_person(self, person_id: str) -> None:
        self._session.execute(
            delete(FotosFaceReferenceModel).where(
                FotosFaceReferenceModel.person_id == person_id
            )
        )
        self._session.execute(
            update(FotosFaceModel)
            .where(FotosFaceModel.person_id == person_id)
            .values(person_id=None, status="unknown", confidence=None)
        )
