from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from deja_indicadores_api.companies.exceptions import CompanyNotFoundError
from deja_indicadores_api.companies.repository import CompanyRepository
from deja_indicadores_api.dashboards.exceptions import (
    InvalidDashboardPeriodError,
)
from deja_indicadores_api.dashboards.repository import DashboardRepository
from deja_indicadores_api.dashboards.schemas import (
    DashboardIndicator,
    DashboardMeasurement,
    DashboardOverviewResponse,
    DashboardSituation,
    DashboardStatusCount,
    DashboardTotals,
)
from deja_indicadores_api.indicators.models import (
    IndicatorDirection,
    IndicatorModel,
)
from deja_indicadores_api.measurements.models import MeasurementModel


class DashboardService:
    """Regras de aplicação do dashboard gerencial."""

    def __init__(
        self,
        repository: DashboardRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self._repository = repository
        self._company_repository = company_repository

    def get_overview(
        self,
        company_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DashboardOverviewResponse:
        """Retorna a visão gerencial consolidada."""

        self._validate_period(start_date, end_date)

        if company_id is not None:
            self._ensure_company_exists(company_id)

        indicators = [
            self._build_indicator(
                indicator,
                company.trade_name,
                start_date,
                end_date,
            )
            for indicator, company in self._repository.list_indicators(
                company_id
            )
        ]

        return DashboardOverviewResponse(
            totals=DashboardTotals(
                companies=self._repository.count_companies(company_id),
                indicators=self._repository.count_indicators(company_id),
                measurements=self._repository.count_measurements(
                    company_id,
                    start_date,
                    end_date,
                ),
            ),
            companies_by_status=[
                DashboardStatusCount(
                    status=status.value,
                    count=count,
                )
                for status, count
                in self._repository.count_companies_by_status(company_id)
            ],
            indicators_by_status=[
                DashboardStatusCount(
                    status=status.value,
                    count=count,
                )
                for status, count
                in self._repository.count_indicators_by_status(company_id)
            ],
            indicators=indicators,
        )

    def _build_indicator(
        self,
        indicator: IndicatorModel,
        company_trade_name: str,
        start_date: date | None,
        end_date: date | None,
    ) -> DashboardIndicator:
        """Monta a visão gerencial de um indicador."""

        measurements = self._repository.list_measurements_by_indicator(
            indicator.id,
            start_date,
            end_date,
        )
        current_measurement = measurements[-1] if measurements else None

        return DashboardIndicator(
            id=indicator.id,
            company_id=indicator.company_id,
            company_trade_name=company_trade_name,
            name=indicator.name,
            unit=indicator.unit,
            direction=indicator.direction,
            status=indicator.status,
            target_value=indicator.target_value,
            current_measurement=self._to_dashboard_measurement(
                current_measurement
            ),
            achievement_percentage=self._calculate_achievement_percentage(
                indicator,
                current_measurement,
            ),
            situation=self._determine_situation(
                indicator,
                current_measurement,
            ),
            history=[
                self._to_dashboard_measurement(measurement)
                for measurement in measurements
            ],
        )

    @staticmethod
    def _to_dashboard_measurement(
        measurement: MeasurementModel | None,
    ) -> DashboardMeasurement | None:
        """Converte uma medição persistente para o contrato gerencial."""

        if measurement is None:
            return None

        return DashboardMeasurement.model_validate(measurement)

    @staticmethod
    def _calculate_achievement_percentage(
        indicator: IndicatorModel,
        measurement: MeasurementModel | None,
    ) -> Decimal | None:
        """Calcula o percentual de atingimento da meta."""

        if measurement is None:
            return None

        actual_value = measurement.actual_value
        target_value = indicator.target_value

        if indicator.direction == IndicatorDirection.HIGHER_IS_BETTER:
            if target_value == 0:
                return None

            percentage = actual_value / target_value * Decimal("100")
        else:
            if actual_value == 0:
                return None

            percentage = target_value / actual_value * Decimal("100")

        return percentage.quantize(
            Decimal("0.0001"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _determine_situation(
        indicator: IndicatorModel,
        measurement: MeasurementModel | None,
    ) -> DashboardSituation:
        """Determina a situação atual do indicador perante sua meta."""

        if measurement is None:
            return DashboardSituation.NO_DATA

        actual_value = measurement.actual_value
        target_value = indicator.target_value

        if actual_value == target_value:
            return DashboardSituation.ON_TARGET

        if indicator.direction == IndicatorDirection.HIGHER_IS_BETTER:
            if actual_value > target_value:
                return DashboardSituation.ON_TARGET

            return DashboardSituation.BELOW_TARGET

        if actual_value < target_value:
            return DashboardSituation.ON_TARGET

        return DashboardSituation.ABOVE_TARGET

    @staticmethod
    def _validate_period(
        start_date: date | None,
        end_date: date | None,
    ) -> None:
        """Garante que o período informado seja coerente."""

        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise InvalidDashboardPeriodError()

    def _ensure_company_exists(self, company_id: str) -> None:
        """Garante que a empresa informada esteja cadastrada."""

        company = self._company_repository.find_by_id(company_id)

        if company is None:
            raise CompanyNotFoundError(company_id)