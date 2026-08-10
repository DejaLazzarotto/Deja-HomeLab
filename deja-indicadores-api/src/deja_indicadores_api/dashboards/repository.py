from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from deja_indicadores_api.companies.models import CompanyModel
from deja_indicadores_api.indicators.models import IndicatorModel
from deja_indicadores_api.measurements.models import MeasurementModel


class DashboardRepository:
    """Consultas de leitura para o dashboard gerencial."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def count_companies(self, company_id: str | None = None) -> int:
        """Conta empresas dentro do recorte informado."""

        statement = select(func.count(CompanyModel.id))

        if company_id is not None:
            statement = statement.where(CompanyModel.id == company_id)

        return int(self._session.scalar(statement) or 0)

    def count_indicators(self, company_id: str | None = None) -> int:
        """Conta indicadores dentro do recorte informado."""

        statement = select(func.count(IndicatorModel.id))

        if company_id is not None:
            statement = statement.where(
                IndicatorModel.company_id == company_id
            )

        return int(self._session.scalar(statement) or 0)

    def count_measurements(
        self,
        company_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """Conta medições dentro do recorte informado."""

        statement = (
            select(func.count(MeasurementModel.id))
            .join(
                IndicatorModel,
                MeasurementModel.indicator_id == IndicatorModel.id,
            )
        )

        if company_id is not None:
            statement = statement.where(
                IndicatorModel.company_id == company_id
            )

        statement = self._apply_measurement_period(
            statement,
            start_date,
            end_date,
        )

        return int(self._session.scalar(statement) or 0)

    def count_companies_by_status(
        self,
        company_id: str | None = None,
    ) -> list[tuple[object, int]]:
        """Agrupa empresas por status."""

        statement = select(
            CompanyModel.status,
            func.count(CompanyModel.id),
        ).group_by(CompanyModel.status)

        if company_id is not None:
            statement = statement.where(CompanyModel.id == company_id)

        statement = statement.order_by(CompanyModel.status)
        return [(status, int(count)) for status, count in self._session.execute(
            statement
        ).all()]

    def count_indicators_by_status(
        self,
        company_id: str | None = None,
    ) -> list[tuple[object, int]]:
        """Agrupa indicadores por status."""

        statement = select(
            IndicatorModel.status,
            func.count(IndicatorModel.id),
        ).group_by(IndicatorModel.status)

        if company_id is not None:
            statement = statement.where(
                IndicatorModel.company_id == company_id
            )

        statement = statement.order_by(IndicatorModel.status)
        return [(status, int(count)) for status, count in self._session.execute(
            statement
        ).all()]

    def list_indicators(
        self,
        company_id: str | None = None,
    ) -> list[tuple[IndicatorModel, CompanyModel]]:
        """Lista indicadores acompanhados de suas empresas."""

        statement = (
            select(IndicatorModel, CompanyModel)
            .join(
                CompanyModel,
                IndicatorModel.company_id == CompanyModel.id,
            )
        )

        if company_id is not None:
            statement = statement.where(
                IndicatorModel.company_id == company_id
            )

        statement = statement.order_by(
            CompanyModel.trade_name,
            IndicatorModel.name,
            IndicatorModel.id,
        )

        return list(self._session.execute(statement).all())

    def list_measurements_by_indicator(
        self,
        indicator_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MeasurementModel]:
        """Lista o histórico de um indicador dentro do período."""

        statement = select(MeasurementModel).where(
            MeasurementModel.indicator_id == indicator_id
        )

        statement = self._apply_measurement_period(
            statement,
            start_date,
            end_date,
        )

        statement = statement.order_by(
            MeasurementModel.reference_date,
            MeasurementModel.id,
        )

        return list(self._session.scalars(statement).all())

    @staticmethod
    def _apply_measurement_period(
        statement: Select,
        start_date: date | None,
        end_date: date | None,
    ) -> Select:
        """Aplica datas inicial e final inclusivas à consulta."""

        if start_date is not None:
            statement = statement.where(
                MeasurementModel.reference_date >= start_date
            )

        if end_date is not None:
            statement = statement.where(
                MeasurementModel.reference_date <= end_date
            )

        return statement