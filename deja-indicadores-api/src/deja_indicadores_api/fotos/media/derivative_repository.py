from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.fotos.media.derivative_models import (
    FotosMediaDerivativeModel,
)


class FotosMediaDerivativeRepository:
    """Persistência dos arquivos derivados de mídias."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def list_by_media_id(
        self,
        media_id: str,
    ) -> list[FotosMediaDerivativeModel]:
        """Lista todos os derivados de uma mídia."""

        statement = (
            select(FotosMediaDerivativeModel)
            .where(
                FotosMediaDerivativeModel.media_id == media_id
            )
            .order_by(
                FotosMediaDerivativeModel.derivative_type.asc(),
                FotosMediaDerivativeModel.created_at.asc(),
                FotosMediaDerivativeModel.id.asc(),
            )
        )

        return list(
            self._session.scalars(
                statement
            ).all()
        )

    def find_by_media_and_type(
        self,
        media_id: str,
        derivative_type: str,
    ) -> FotosMediaDerivativeModel | None:
        """Retorna um derivado específico de uma mídia."""

        statement = (
            select(FotosMediaDerivativeModel)
            .where(
                FotosMediaDerivativeModel.media_id == media_id,
                FotosMediaDerivativeModel.derivative_type
                == derivative_type,
            )
        )

        return self._session.scalar(
            statement
        )

    def add(
        self,
        derivative: FotosMediaDerivativeModel,
    ) -> FotosMediaDerivativeModel:
        """Persiste um novo derivado."""

        self._session.add(
            derivative
        )
        self._session.commit()
        self._session.refresh(
            derivative
        )

        return derivative

    def delete(
        self,
        derivative: FotosMediaDerivativeModel,
    ) -> None:
        """Remove um derivado persistido."""

        self._session.delete(
            derivative
        )
        self._session.commit()