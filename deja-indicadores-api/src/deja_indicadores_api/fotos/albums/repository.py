from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.albums.models import (
    FotosAlbumModel,
    FotosAlbumPeriodDescriptionModel,
)
from deja_indicadores_api.fotos.media.models import (
    FotosMediaModel,
)

FotosAlbumPeriodRow = tuple[
    int | None,
    int | None,
    int,
    str | None,
]


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

    def list_periods(
        self,
        album_id: str,
    ) -> list[FotosAlbumPeriodRow]:
        """Lista os períodos reais de um álbum com suas quantidades."""

        year_expression = extract(
            "year",
            FotosMediaModel.original_date,
        )
        month_expression = extract(
            "month",
            FotosMediaModel.original_date,
        )

        media_periods = (
            select(
                year_expression.label("year"),
                month_expression.label("month"),
                func.count(
                    FotosMediaModel.id
                ).label("media_count"),
            )
            .where(
                FotosMediaModel.album_id == album_id,
                FotosMediaModel.deleted_at.is_(None),
            )
            .group_by(
                year_expression,
                month_expression,
            )
            .subquery()
        )

        statement = (
            select(
                media_periods.c.year,
                media_periods.c.month,
                media_periods.c.media_count,
                FotosAlbumPeriodDescriptionModel.description,
            )
            .outerjoin(
                FotosAlbumPeriodDescriptionModel,
                (
                    FotosAlbumPeriodDescriptionModel.album_id
                    == album_id
                )
                & (
                    FotosAlbumPeriodDescriptionModel.original_year
                    == media_periods.c.year
                )
                & (
                    FotosAlbumPeriodDescriptionModel.original_month
                    == media_periods.c.month
                ),
            )
            .order_by(
                media_periods.c.year.is_(None),
                media_periods.c.year.desc(),
                media_periods.c.month.desc(),
            )
        )

        rows = self._session.execute(
            statement
        ).all()

        return [
            (
                int(row.year)
                if row.year is not None
                else None,
                int(row.month)
                if row.month is not None
                else None,
                int(row.media_count),
                row.description,
            )
            for row in rows
        ]

    def period_exists(
        self,
        *,
        album_id: str,
        year: int,
        month: int,
    ) -> bool:
        """Verifica se o álbum possui mídia ativa no período."""

        statement = select(
            func.count(FotosMediaModel.id)
        ).where(
            FotosMediaModel.album_id == album_id,
            FotosMediaModel.deleted_at.is_(None),
            extract(
                "year",
                FotosMediaModel.original_date,
            )
            == year,
            extract(
                "month",
                FotosMediaModel.original_date,
            )
            == month,
        )

        return bool(
            self._session.scalar(statement)
        )

    def find_period_description(
        self,
        *,
        album_id: str,
        year: int,
        month: int,
    ) -> FotosAlbumPeriodDescriptionModel | None:
        """Localiza a descrição persistida de um período."""

        statement = select(
            FotosAlbumPeriodDescriptionModel
        ).where(
            FotosAlbumPeriodDescriptionModel.album_id
            == album_id,
            FotosAlbumPeriodDescriptionModel.original_year
            == year,
            FotosAlbumPeriodDescriptionModel.original_month
            == month,
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

    def save_period_description(
        self,
        period_description: FotosAlbumPeriodDescriptionModel,
    ) -> FotosAlbumPeriodDescriptionModel:
        """Persiste a descrição mensal de um álbum."""

        self._session.add(period_description)
        self._session.commit()
        self._session.refresh(period_description)

        return period_description

    def delete_period_description(
        self,
        period_description: FotosAlbumPeriodDescriptionModel,
    ) -> None:
        """Remove uma descrição mensal persistida."""

        self._session.delete(period_description)
        self._session.commit()

    def delete(
        self,
        album: FotosAlbumModel,
    ) -> None:
        """Remove um álbum persistentemente."""

        self._session.delete(album)
        self._session.commit()