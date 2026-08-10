from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.indicators.models import IndicatorModel


class IndicatorRepository:
    """Acesso persistente aos indicadores cadastrados."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self, company_id: str | None = None) -> list[IndicatorModel]:
        """Lista indicadores, opcionalmente filtrados por empresa."""

        statement = select(IndicatorModel)

        if company_id is not None:
            statement = statement.where(
                IndicatorModel.company_id == company_id
            )

        statement = statement.order_by(IndicatorModel.name)
        return list(self._session.scalars(statement).all())

    def find_by_id(self, indicator_id: str) -> IndicatorModel | None:
        """Localiza um indicador pelo identificador."""

        return self._session.get(IndicatorModel, indicator_id)

    def find_by_company_and_name(
        self,
        company_id: str,
        name: str,
    ) -> IndicatorModel | None:
        """Localiza um indicador pelo nome dentro da empresa."""

        statement = select(IndicatorModel).where(
            IndicatorModel.company_id == company_id,
            IndicatorModel.name == name,
        )
        return self._session.scalar(statement)

    def exists_for_company(self, company_id: str) -> bool:
        """Verifica se a empresa possui algum indicador."""

        statement = (
            select(IndicatorModel.id)
            .where(IndicatorModel.company_id == company_id)
            .limit(1)
        )
        return self._session.scalar(statement) is not None

    def add(self, indicator: IndicatorModel) -> IndicatorModel:
        """Adiciona e persiste um indicador."""

        self._session.add(indicator)
        self._session.commit()
        self._session.refresh(indicator)
        return indicator

    def update(self, indicator: IndicatorModel) -> IndicatorModel:
        """Persiste as alterações realizadas em um indicador."""

        self._session.commit()
        self._session.refresh(indicator)
        return indicator

    def delete(self, indicator: IndicatorModel) -> None:
        """Remove um indicador persistentemente."""

        self._session.delete(indicator)
        self._session.commit()