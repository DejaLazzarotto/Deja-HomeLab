from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.albums.models import (
    FotosAlbumModel,
)


class FotosAlbumRepository:
    """Acesso persistente aos álbuns do Deja Fotos."""

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
        active: bool | None = None,
    ) -> list[FotosAlbumModel]:
        """Lista álbuns dentro dos filtros informados."""

        statement = select(FotosAlbumModel)

        if organization_id is not None:
            statement = statement.where(
                FotosAlbumModel.organization_id
                == organization_id
            )

        if tenant_id is not None:
            statement = statement.where(
                FotosAlbumModel.tenant_id
                == tenant_id
            )

        if environment_id is not None:
            statement = statement.where(
                FotosAlbumModel.environment_id
                == environment_id
            )

        if active is not None:
            statement = statement.where(
                FotosAlbumModel.active == active
            )

        statement = statement.order_by(
            FotosAlbumModel.name
        )

        return list(
            self._session.scalars(statement).all()
        )

    def find_by_id(
        self,
        album_id: str,
    ) -> FotosAlbumModel | None:
        """Localiza um álbum pelo identificador."""

        return self._session.get(
            FotosAlbumModel,
            album_id,
        )

    def find_by_scope_and_name(
        self,
        *,
        organization_id: str,
        tenant_id: str,
        environment_id: str,
        name: str,
    ) -> FotosAlbumModel | None:
        """Localiza um álbum pelo nome dentro do escopo."""

        statement = select(
            FotosAlbumModel
        ).where(
            FotosAlbumModel.organization_id
            == organization_id,
            FotosAlbumModel.tenant_id
            == tenant_id,
            FotosAlbumModel.environment_id
            == environment_id,
            FotosAlbumModel.name
            == name,
        )

        return self._session.scalar(statement)

    def add(
        self,
        album: FotosAlbumModel,
    ) -> FotosAlbumModel:
        """Adiciona e persiste um álbum."""

        self._session.add(album)
        self._session.commit()
        self._session.refresh(album)

        return album

    def update(
        self,
        album: FotosAlbumModel,
    ) -> FotosAlbumModel:
        """Persiste as alterações de um álbum."""

        self._session.commit()
        self._session.refresh(album)

        return album

    def delete(
        self,
        album: FotosAlbumModel,
    ) -> None:
        """Remove um álbum persistentemente."""

        self._session.delete(album)
        self._session.commit()