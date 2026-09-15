from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.media.models import (
    FotosMediaModel,
)


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
        include_deleted: bool = False,
    ) -> list[FotosMediaModel]:
        """Lista mídias dentro dos filtros informados."""

        statement = select(FotosMediaModel)

        if organization_id is not None:
            statement = statement.where(
                FotosMediaModel.organization_id
                == organization_id
            )

        if tenant_id is not None:
            statement = statement.where(
                FotosMediaModel.tenant_id
                == tenant_id
            )

        if environment_id is not None:
            statement = statement.where(
                FotosMediaModel.environment_id
                == environment_id
            )

        if album_id is not None:
            statement = statement.where(
                FotosMediaModel.album_id
                == album_id
            )

        if media_type is not None:
            statement = statement.where(
                FotosMediaModel.media_type
                == media_type
            )

        if processing_status is not None:
            statement = statement.where(
                FotosMediaModel.processing_status
                == processing_status
            )

        if not include_deleted:
            statement = statement.where(
                FotosMediaModel.deleted_at.is_(None)
            )

        statement = statement.order_by(
            FotosMediaModel.original_date.desc(),
            FotosMediaModel.created_at.desc(),
            FotosMediaModel.id.asc(),
        )

        return list(
            self._session.scalars(statement).all()
        )

    def find_by_id(
        self,
        media_id: str,
        *,
        include_deleted: bool = False,
    ) -> FotosMediaModel | None:
        """Localiza uma mídia pelo identificador."""

        statement = select(
            FotosMediaModel
        ).where(
            FotosMediaModel.id == media_id
        )

        if not include_deleted:
            statement = statement.where(
                FotosMediaModel.deleted_at.is_(None)
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

        statement = select(
            FotosMediaModel
        ).where(
            FotosMediaModel.checksum_sha256
            == checksum_sha256,
            FotosMediaModel.deleted_at.is_(None),
        )

        if organization_id is not None:
            statement = statement.where(
                FotosMediaModel.organization_id
                == organization_id
            )

        if tenant_id is not None:
            statement = statement.where(
                FotosMediaModel.tenant_id
                == tenant_id
            )

        if environment_id is not None:
            statement = statement.where(
                FotosMediaModel.environment_id
                == environment_id
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

        return bool(
            self._session.scalar(statement)
        )

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