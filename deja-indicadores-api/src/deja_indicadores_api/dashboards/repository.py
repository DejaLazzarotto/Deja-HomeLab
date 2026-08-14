from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from deja_indicadores_api.companies.models import CompanyModel
from deja_indicadores_api.indicators.models import IndicatorModel
from deja_indicadores_api.measurements.models import MeasurementModel
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    TenantModel,
)


class DashboardRepository:
    """Consultas institucionais de leitura para o dashboard gerencial."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def count_companies(
        self,
        *,
        company_id: str | None = None,
        indicator_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> int:
        """Conta empresas dentro do escopo e dos filtros informados."""

        statement = (
            select(func.count(func.distinct(CompanyModel.id)))
            .join(
                EnvironmentModel,
                CompanyModel.environment_id == EnvironmentModel.id,
            )
            .join(
                TenantModel,
                EnvironmentModel.tenant_id == TenantModel.id,
            )
        )

        if indicator_id is not None:
            statement = statement.join(
                IndicatorModel,
                IndicatorModel.company_id == CompanyModel.id,
            ).where(IndicatorModel.id == indicator_id)

        if company_id is not None:
            statement = statement.where(CompanyModel.id == company_id)

        statement = self._apply_institutional_scope(
            statement,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )

        return int(self._session.scalar(statement) or 0)

    def count_indicators(
        self,
        *,
        company_id: str | None = None,
        indicator_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> int:
        """Conta indicadores dentro do escopo e dos filtros informados."""

        statement = (
            select(func.count(IndicatorModel.id))
            .join(
                CompanyModel,
                IndicatorModel.company_id == CompanyModel.id,
            )
            .join(
                EnvironmentModel,
                CompanyModel.environment_id == EnvironmentModel.id,
            )
            .join(
                TenantModel,
                EnvironmentModel.tenant_id == TenantModel.id,
            )
        )
        statement = self._apply_resource_filters(
            statement,
            company_id=company_id,
            indicator_id=indicator_id,
        )
        statement = self._apply_institutional_scope(
            statement,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )

        return int(self._session.scalar(statement) or 0)

    def count_measurements(
        self,
        *,
        company_id: str | None = None,
        indicator_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """Conta medições dentro do escopo, dos filtros e do período."""

        statement = (
            select(func.count(MeasurementModel.id))
            .join(
                IndicatorModel,
                MeasurementModel.indicator_id == IndicatorModel.id,
            )
            .join(
                CompanyModel,
                IndicatorModel.company_id == CompanyModel.id,
            )
            .join(
                EnvironmentModel,
                CompanyModel.environment_id == EnvironmentModel.id,
            )
            .join(
                TenantModel,
                EnvironmentModel.tenant_id == TenantModel.id,
            )
        )
        statement = self._apply_resource_filters(
            statement,
            company_id=company_id,
            indicator_id=indicator_id,
        )
        statement = self._apply_institutional_scope(
            statement,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )
        statement = self._apply_measurement_period(
            statement,
            start_date,
            end_date,
        )

        return int(self._session.scalar(statement) or 0)

    def count_companies_by_status(
        self,
        *,
        company_id: str | None = None,
        indicator_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> list[tuple[object, int]]:
        """Agrupa empresas autorizadas por status."""

        statement = (
            select(
                CompanyModel.status,
                func.count(func.distinct(CompanyModel.id)),
            )
            .join(
                EnvironmentModel,
                CompanyModel.environment_id == EnvironmentModel.id,
            )
            .join(
                TenantModel,
                EnvironmentModel.tenant_id == TenantModel.id,
            )
            .group_by(CompanyModel.status)
        )

        if indicator_id is not None:
            statement = statement.join(
                IndicatorModel,
                IndicatorModel.company_id == CompanyModel.id,
            ).where(IndicatorModel.id == indicator_id)

        if company_id is not None:
            statement = statement.where(CompanyModel.id == company_id)

        statement = self._apply_institutional_scope(
            statement,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )
        statement = statement.order_by(CompanyModel.status)

        return [
            (status, int(count))
            for status, count in self._session.execute(statement).all()
        ]

    def count_indicators_by_status(
        self,
        *,
        company_id: str | None = None,
        indicator_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> list[tuple[object, int]]:
        """Agrupa indicadores autorizados por status."""

        statement = (
            select(
                IndicatorModel.status,
                func.count(IndicatorModel.id),
            )
            .join(
                CompanyModel,
                IndicatorModel.company_id == CompanyModel.id,
            )
            .join(
                EnvironmentModel,
                CompanyModel.environment_id == EnvironmentModel.id,
            )
            .join(
                TenantModel,
                EnvironmentModel.tenant_id == TenantModel.id,
            )
            .group_by(IndicatorModel.status)
        )
        statement = self._apply_resource_filters(
            statement,
            company_id=company_id,
            indicator_id=indicator_id,
        )
        statement = self._apply_institutional_scope(
            statement,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )
        statement = statement.order_by(IndicatorModel.status)

        return [
            (status, int(count))
            for status, count in self._session.execute(statement).all()
        ]

    def list_indicators(
        self,
        *,
        company_id: str | None = None,
        indicator_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
    ) -> list[tuple[IndicatorModel, CompanyModel]]:
        """Lista indicadores acompanhados de empresas autorizadas."""

        statement = (
            select(IndicatorModel, CompanyModel)
            .join(
                CompanyModel,
                IndicatorModel.company_id == CompanyModel.id,
            )
            .join(
                EnvironmentModel,
                CompanyModel.environment_id == EnvironmentModel.id,
            )
            .join(
                TenantModel,
                EnvironmentModel.tenant_id == TenantModel.id,
            )
        )
        statement = self._apply_resource_filters(
            statement,
            company_id=company_id,
            indicator_id=indicator_id,
        )
        statement = self._apply_institutional_scope(
            statement,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
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
        *,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[MeasurementModel]:
        """Lista o histórico autorizado de um indicador no período."""

        statement = (
            select(MeasurementModel)
            .join(
                IndicatorModel,
                MeasurementModel.indicator_id == IndicatorModel.id,
            )
            .join(
                CompanyModel,
                IndicatorModel.company_id == CompanyModel.id,
            )
            .join(
                EnvironmentModel,
                CompanyModel.environment_id == EnvironmentModel.id,
            )
            .join(
                TenantModel,
                EnvironmentModel.tenant_id == TenantModel.id,
            )
            .where(MeasurementModel.indicator_id == indicator_id)
        )
        statement = self._apply_institutional_scope(
            statement,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
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
    def _apply_resource_filters(
        statement: Select,
        *,
        company_id: str | None,
        indicator_id: str | None,
    ) -> Select:
        """Aplica filtros de empresa e indicador."""

        if company_id is not None:
            statement = statement.where(
                IndicatorModel.company_id == company_id
            )

        if indicator_id is not None:
            statement = statement.where(IndicatorModel.id == indicator_id)

        return statement

    @staticmethod
    def _apply_institutional_scope(
        statement: Select,
        *,
        organization_id: str | None,
        tenant_id: str | None,
        environment_id: str | None,
    ) -> Select:
        """Aplica o escopo institucional diretamente à consulta."""

        if organization_id is not None:
            statement = statement.where(
                TenantModel.organization_id == organization_id
            )

        if tenant_id is not None:
            statement = statement.where(TenantModel.id == tenant_id)

        if environment_id is not None:
            statement = statement.where(
                EnvironmentModel.id == environment_id
            )

        return statement

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