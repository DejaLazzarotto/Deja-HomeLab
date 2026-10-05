from datetime import datetime

from sqlalchemy import exists, extract, func, or_, select, update
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.curation.models import (
    FotosFaceModel,
    FotosFaceReferenceModel,
)
from deja_indicadores_api.fotos.media.models import (
    FotosMediaModel,
)

FotosMediaPeriodRow = tuple[
    int,
    int,
    int,
]


class FotosMediaRepository:
    """Acesso persistente às mídias do Deja Fotos."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def list(
        self,
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
        """Lista uma página de mídias e retorna o total filtrado."""

        conditions = []

        if organization_id is not None:
            conditions.append(FotosMediaModel.organization_id == organization_id)

        if tenant_id is not None:
            conditions.append(FotosMediaModel.tenant_id == tenant_id)

        if environment_id is not None:
            conditions.append(FotosMediaModel.environment_id == environment_id)

        if album_id is not None:
            conditions.append(FotosMediaModel.album_id == album_id)

        if media_type is not None:
            conditions.append(FotosMediaModel.media_type == media_type)

        if processing_status is not None:
            conditions.append(FotosMediaModel.processing_status == processing_status)

        if original_date_from is not None:
            conditions.append(FotosMediaModel.original_date >= original_date_from)

        if original_date_to is not None:
            conditions.append(FotosMediaModel.original_date <= original_date_to)

        if original_year is not None:
            conditions.append(
                extract(
                    "year",
                    FotosMediaModel.original_date,
                )
                == original_year
            )

        if original_month is not None:
            conditions.append(
                extract(
                    "month",
                    FotosMediaModel.original_date,
                )
                == original_month
            )

        if without_original_date:
            conditions.append(FotosMediaModel.original_date.is_(None))

        if original_date_verified is not None:
            conditions.append(FotosMediaModel.original_date_verified == original_date_verified)

        if original_date_conflict is not None:
            conditions.append(FotosMediaModel.original_date_conflict == original_date_conflict)

        if was_converted is not None:
            conditions.append(FotosMediaModel.was_converted == was_converted)

        if not include_deleted:
            conditions.append(FotosMediaModel.deleted_at.is_(None))

        count_statement = select(func.count(FotosMediaModel.id)).where(*conditions)

        total = int(self._session.scalar(count_statement) or 0)

        statement = (
            select(FotosMediaModel)
            .where(*conditions)
            .order_by(
                FotosMediaModel.original_date.desc(),
                FotosMediaModel.created_at.desc(),
                FotosMediaModel.id.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        items = list(self._session.scalars(statement).all())

        return items, total

    def list_periods(
        self,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> list[FotosMediaPeriodRow]:
        """Lista os períodos reais existentes no acervo com suas quantidades."""

        year_expression = extract(
            "year",
            FotosMediaModel.original_date,
        )
        month_expression = extract(
            "month",
            FotosMediaModel.original_date,
        )

        conditions = [
            FotosMediaModel.deleted_at.is_(None),
            FotosMediaModel.original_date.is_not(None),
        ]

        if organization_id is not None:
            conditions.append(
                FotosMediaModel.organization_id
                == organization_id
            )

        if tenant_id is not None:
            conditions.append(
                FotosMediaModel.tenant_id
                == tenant_id
            )

        if environment_id is not None:
            conditions.append(
                FotosMediaModel.environment_id
                == environment_id
            )

        statement = (
            select(
                year_expression.label("year"),
                month_expression.label("month"),
                func.count(
                    FotosMediaModel.id
                ).label("media_count"),
            )
            .where(*conditions)
            .group_by(
                year_expression,
                month_expression,
            )
            .order_by(
                year_expression.desc(),
                month_expression.desc(),
            )
        )

        rows = self._session.execute(
            statement
        ).all()

        return [
            (
                int(row.year),
                int(row.month),
                int(row.media_count),
            )
            for row in rows
        ]
    def find_by_id(
        self,
        media_id: str,
        *,
        include_deleted: bool = False,
    ) -> FotosMediaModel | None:
        """Localiza uma mídia pelo identificador."""

        statement = select(FotosMediaModel).where(FotosMediaModel.id == media_id)

        if not include_deleted:
            statement = statement.where(FotosMediaModel.deleted_at.is_(None))

        return self._session.scalar(statement)

    def find_by_id_for_update(
        self,
        media_id: str,
    ) -> FotosMediaModel | None:
        """Localiza e bloqueia uma m?dia ativa para atualiza??o."""

        statement = (
            select(FotosMediaModel)
            .where(
                FotosMediaModel.id == media_id,
                FotosMediaModel.deleted_at.is_(None),
            )
            .with_for_update()
        )

        return self._session.scalar(statement)

    def find_by_checksum(
        self,
        checksum_sha256: str,
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> FotosMediaModel | None:
        """Localiza mídia ativa pelo checksum SHA-256."""

        statement = select(FotosMediaModel).where(
            FotosMediaModel.checksum_sha256 == checksum_sha256,
            FotosMediaModel.deleted_at.is_(None),
        )

        if organization_id is not None:
            statement = statement.where(FotosMediaModel.organization_id == organization_id)

        if tenant_id is not None:
            statement = statement.where(FotosMediaModel.tenant_id == tenant_id)

        if environment_id is not None:
            statement = statement.where(FotosMediaModel.environment_id == environment_id)

        return self._session.scalar(statement)

    def find_by_source_checksum(
        self,
        source_checksum_sha256: str,
        *,
        environment_id: str,
    ) -> FotosMediaModel | None:
        """Localiza mídia pelo checksum da fonte no ambiente."""

        statement = (
            select(FotosMediaModel)
            .where(
                FotosMediaModel.environment_id == environment_id,
                FotosMediaModel.source_checksum_sha256 == source_checksum_sha256,
            )
            .order_by(
                FotosMediaModel.deleted_at.asc(),
                FotosMediaModel.created_at.asc(),
            )
        )

        return self._session.scalar(statement)

    def exists_by_album_id(
        self,
        album_id: str,
    ) -> bool:
        """Verifica se o álbum possui mídia ativa vinculada."""

        statement = select(
            exists().where(
                FotosMediaModel.album_id == album_id,
                FotosMediaModel.deleted_at.is_(None),
            )
        )

        return bool(self._session.scalar(statement))

    def add(
        self,
        media: FotosMediaModel,
    ) -> FotosMediaModel:
        """Adiciona e persiste uma mídia."""

        self._session.add(media)
        self._session.commit()
        self._session.refresh(media)

        return media

    def update(
        self,
        media: FotosMediaModel,
    ) -> FotosMediaModel:
        """Persiste alterações de uma mídia."""

        self._session.commit()
        self._session.refresh(media)

        return media

    def rollback(self) -> None:
        """Desfaz a transa??o atual e libera seus bloqueios."""

        self._session.rollback()

    def reference_keys_for_media(self, media_id: str) -> list[str]:
        """Obtém somente as referências dos rostos desta mídia."""

        statement = (
            select(FotosFaceReferenceModel.storage_key)
            .join(FotosFaceModel, FotosFaceModel.id == FotosFaceReferenceModel.face_id)
            .where(FotosFaceModel.media_id == media_id)
        )
        return list(self._session.scalars(statement))

    def delete_permanently(self, media: FotosMediaModel) -> None:
        """Remove a mídia; chaves estrangeiras em cascata removem apenas seus filhos."""

        self._session.delete(media)
        self._session.commit()

    def try_start_processing(
        self,
        media: FotosMediaModel,
        *,
        stale_before: datetime,
        started_at: datetime,
    ) -> bool:
        """Assume atomicamente um processamento permitido ou abandonado."""

        statement = (
            update(FotosMediaModel)
            .where(
                FotosMediaModel.id == media.id,
                or_(
                    FotosMediaModel.processing_status != "processing",
                    FotosMediaModel.updated_at <= stale_before,
                ),
            )
            .values(
                processing_status="processing",
                processing_error=None,
                updated_at=started_at,
            )
        )

        result = self._session.execute(statement)
        self._session.commit()
        self._session.refresh(media)

        return result.rowcount == 1
