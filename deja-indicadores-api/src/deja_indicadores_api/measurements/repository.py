from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from deja_indicadores_api.indicators.models import IndicatorModel
from deja_indicadores_api.measurements.models import MeasurementModel


class MeasurementRepository:
    """Acesso persistente às medições manuais dos indicadores."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self,
        company_id: str | None = None,
        indicator_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MeasurementModel]:
        """Lista medições de acordo com os filtros informados."""

        statement = select(MeasurementModel)

        if company_id is not None:
            statement = statement.join(
                IndicatorModel,
                MeasurementModel.indicator_id == IndicatorModel.id,
            ).where(IndicatorModel.company_id == company_id)

        if indicator_id is not None:
            statement = statement.where(
                MeasurementModel.indicator_id == indicator_id
            )

        if start_date is not None:
            statement = statement.where(
                MeasurementModel.reference_date >= start_date
            )

        if end_date is not None:
            statement = statement.where(
                MeasurementModel.reference_date <= end_date
            )

        statement = statement.order_by(
            MeasurementModel.reference_date,
            MeasurementModel.id,
        )

        return list(self._session.scalars(statement).all())

    def find_by_id(
        self,
        measurement_id: str,
    ) -> MeasurementModel | None:
        """Localiza uma medição pelo identificador."""

        return self._session.get(MeasurementModel, measurement_id)

    def find_by_indicator_and_reference_date(
        self,
        indicator_id: str,
        reference_date: date,
    ) -> MeasurementModel | None:
        """Localiza uma medição pelo indicador e data de referência."""

        statement = select(MeasurementModel).where(
            MeasurementModel.indicator_id == indicator_id,
            MeasurementModel.reference_date == reference_date,
        )

        return self._session.scalar(statement)

    def exists_for_indicator(self, indicator_id: str) -> bool:
        """Verifica se o indicador possui alguma medição."""

        statement = (
            select(MeasurementModel.id)
            .where(MeasurementModel.indicator_id == indicator_id)
            .limit(1)
        )

        return self._session.scalar(statement) is not None

    def add(
        self,
        measurement: MeasurementModel,
    ) -> MeasurementModel:
        """Adiciona e persiste uma medição."""

        self._session.add(measurement)
        self._session.commit()
        self._session.refresh(measurement)
        return measurement

    def update(
        self,
        measurement: MeasurementModel,
    ) -> MeasurementModel:
        """Persiste as alterações realizadas em uma medição."""

        self._session.commit()
        self._session.refresh(measurement)
        return measurement

    def delete(self, measurement: MeasurementModel) -> None:
        """Remove uma medição persistentemente."""

        self._session.delete(measurement)
        self._session.commit()