"""Persistência dos favoritos individuais do Deja Fotos."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from deja_platform_api.fotos.media.favorite_models import (
    FotosMediaFavoriteModel,
)
from deja_platform_api.fotos.media.models import (
    FotosMediaModel,
)


class FotosMediaFavoriteRepository:
    """Gerencia os vínculos entre usuários e mídias favoritas."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def exists(self, user_id: str, media_id: str) -> bool:
        """Verifica se uma mídia está nos favoritos do usuário."""

        statement = select(FotosMediaFavoriteModel.id).where(
            FotosMediaFavoriteModel.user_id == user_id,
            FotosMediaFavoriteModel.media_id == media_id,
        )

        return self._session.scalar(statement) is not None

    def add(
        self,
        favorite: FotosMediaFavoriteModel,
    ) -> FotosMediaFavoriteModel:
        """Persiste um favorito sem permitir vínculos duplicados."""

        if self.exists(favorite.user_id, favorite.media_id):
            return self.find(favorite.user_id, favorite.media_id)

        self._session.add(favorite)

        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            existing = self.find(favorite.user_id, favorite.media_id)

            if existing is not None:
                return existing

            raise

        self._session.refresh(favorite)

        return favorite

    def find(
        self,
        user_id: str,
        media_id: str,
    ) -> FotosMediaFavoriteModel | None:
        """Consulta um vínculo específico do usuário."""

        statement = select(FotosMediaFavoriteModel).where(
            FotosMediaFavoriteModel.user_id == user_id,
            FotosMediaFavoriteModel.media_id == media_id,
        )

        return self._session.scalar(statement)

    def remove(self, user_id: str, media_id: str) -> bool:
        """Remove somente o favorito pertencente ao usuário."""

        favorite = self.find(user_id, media_id)

        if favorite is None:
            return False

        self._session.delete(favorite)
        self._session.commit()

        return True

    def list(
        self,
        user_id: str,
        *,
        page: int = 1,
        page_size: int = 30,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> tuple[list[FotosMediaModel], int]:
        """Lista mídias favoritas ativas do usuário com paginação."""

        conditions = [
            FotosMediaFavoriteModel.user_id == user_id,
            FotosMediaModel.deleted_at.is_(None),
        ]

        if organization_id is not None:
            conditions.append(
                FotosMediaModel.organization_id == organization_id
            )

        if tenant_id is not None:
            conditions.append(
                FotosMediaModel.tenant_id == tenant_id
            )

        if environment_id is not None:
            conditions.append(
                FotosMediaModel.environment_id == environment_id
            )

        count_statement = (
            select(func.count(FotosMediaFavoriteModel.id))
            .join(
                FotosMediaModel,
                FotosMediaModel.id == FotosMediaFavoriteModel.media_id,
            )
            .where(*conditions)
        )

        total = int(self._session.scalar(count_statement) or 0)

        statement = (
            select(FotosMediaModel)
            .join(
                FotosMediaFavoriteModel,
                FotosMediaFavoriteModel.media_id == FotosMediaModel.id,
            )
            .where(*conditions)
            .order_by(
                FotosMediaFavoriteModel.created_at.desc(),
                FotosMediaFavoriteModel.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        items = list(self._session.scalars(statement).all())

        return items, total