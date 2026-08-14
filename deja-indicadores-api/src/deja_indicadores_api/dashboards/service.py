from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from deja_indicadores_api.authentication.authorization import (
    AuthorizationService,
)
from deja_indicadores_api.authentication.schemas import AuthenticatedUser
from deja_indicadores_api.companies.exceptions import CompanyNotFoundError
from deja_indicadores_api.companies.models import CompanyModel
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
from deja_indicadores_api.indicators.exceptions import IndicatorNotFoundError
from deja_indicadores_api.indicators.models import (
    IndicatorDirection,
    IndicatorModel,
)
from deja_indicadores_api.indicators.repository import IndicatorRepository
from deja_indicadores_api.measurements.models import MeasurementModel
from deja_indicadores_api.tenant_management.exceptions import (
    EnvironmentNotFoundError,
    TenantNotFoundError,
)
from deja_indicadores_api.tenant_management.models import (
    EnvironmentModel,
    TenantModel,
)
from deja_indicadores_api.tenant_management.repository import (
    EnvironmentRepository,
    TenantRepository,
)
from deja_indicadores_api.user_management.models import UserRole

DASHBOARD_READER_ROLES = frozenset(
    {
        UserRole.PLATFORM_ADMIN,
        UserRole.ORGANIZATION_ADMIN,
        UserRole.TENANT_ADMIN,
        UserRole.MANAGER,
        UserRole.ANALYST,
        UserRole.VIEWER,
    }
)


class DashboardService:
    """Regras de aplicação do dashboard gerencial."""

    def __init__(
        self,
        repository: DashboardRepository,
        company_repository: CompanyRepository,
        indicator_repository: IndicatorRepository,
        tenant_repository: TenantRepository,
        environment_repository: EnvironmentRepository,
        authorization_service: AuthorizationService,
    ) -> None:
        self._repository = repository
        self._company_repository = company_repository
        self._indicator_repository = indicator_repository
        self._tenant_repository = tenant_repository
        self._environment_repository = environment_repository
        self._authorization_service = authorization_service

    def get_overview(
        self,
        current_user: AuthenticatedUser,
        *,
        company_id: str | None = None,
        indicator_id: str | None = None,
        organization_id: str | None = None,
        tenant_id: str | None = None,
        environment_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DashboardOverviewResponse:
        """Retorna a visão gerencial dentro do escopo permitido."""

        self._require_roles(current_user)
        self._validate_period(start_date, end_date)

        if company_id is not None:
            company = self._require_company(company_id)
            self._require_company_scope(current_user, company)

        if indicator_id is not None:
            indicator = self._require_indicator(indicator_id)
            indicator_company = self._require_company(
                indicator.company_id
            )
            self._require_company_scope(
                current_user,
                indicator_company,
            )

        (
            effective_organization_id,
            effective_tenant_id,
            effective_environment_id,
        ) = self._authorization_service.resolve_list_scope(
            current_user,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
        )

        indicators = [
            self._build_indicator(
                indicator,
                company.trade_name,
                organization_id=effective_organization_id,
                tenant_id=effective_tenant_id,
                environment_id=effective_environment_id,
                start_date=start_date,
                end_date=end_date,
            )
            for indicator, company in self._repository.list_indicators(
                company_id=company_id,
                indicator_id=indicator_id,
                organization_id=effective_organization_id,
                tenant_id=effective_tenant_id,
                environment_id=effective_environment_id,
            )
        ]

        return DashboardOverviewResponse(
            totals=DashboardTotals(
                companies=self._repository.count_companies(
                    company_id=company_id,
                    indicator_id=indicator_id,
                    organization_id=effective_organization_id,
                    tenant_id=effective_tenant_id,
                    environment_id=effective_environment_id,
                ),
                indicators=self._repository.count_indicators(
                    company_id=company_id,
                    indicator_id=indicator_id,
                    organization_id=effective_organization_id,
                    tenant_id=effective_tenant_id,
                    environment_id=effective_environment_id,
                ),
                measurements=self._repository.count_measurements(
                    company_id=company_id,
                    indicator_id=indicator_id,
                    organization_id=effective_organization_id,
                    tenant_id=effective_tenant_id,
                    environment_id=effective_environment_id,
                    start_date=start_date,
                    end_date=end_date,
                ),
            ),
            companies_by_status=[
                DashboardStatusCount(
                    status=status.value,
                    count=count,
                )
                for status, count in (
                    self._repository.count_companies_by_status(
                        company_id=company_id,
                        indicator_id=indicator_id,
                        organization_id=effective_organization_id,
                        tenant_id=effective_tenant_id,
                        environment_id=effective_environment_id,
                    )
                )
            ],
            indicators_by_status=[
                DashboardStatusCount(
                    status=status.value,
                    count=count,
                )
                for status, count in (
                    self._repository.count_indicators_by_status(
                        company_id=company_id,
                        indicator_id=indicator_id,
                        organization_id=effective_organization_id,
                        tenant_id=effective_tenant_id,
                        environment_id=effective_environment_id,
                    )
                )
            ],
            indicators=indicators,
        )

    def _build_indicator(
        self,
        indicator: IndicatorModel,
        company_trade_name: str,
        *,
        organization_id: str | None,
        tenant_id: str | None,
        environment_id: str | None,
        start_date: date | None,
        end_date: date | None,
    ) -> DashboardIndicator:
        """Monta a visão gerencial de um indicador autorizado."""

        measurements = self._repository.list_measurements_by_indicator(
            indicator.id,
            organization_id=organization_id,
            tenant_id=tenant_id,
            environment_id=environment_id,
            start_date=start_date,
            end_date=end_date,
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

    def _require_indicator(self, indicator_id: str) -> IndicatorModel:
        """Garante que o indicador informado esteja cadastrado."""

        indicator = self._indicator_repository.find_by_id(indicator_id)

        if indicator is None:
            raise IndicatorNotFoundError(indicator_id)

        return indicator

    def _require_company(self, company_id: str) -> CompanyModel:
        """Garante que a empresa informada esteja cadastrada."""

        company = self._company_repository.find_by_id(company_id)

        if company is None:
            raise CompanyNotFoundError(company_id)

        return company

    def _require_environment(
        self,
        environment_id: str,
    ) -> EnvironmentModel:
        """Garante que o ambiente institucional exista."""

        environment = self._environment_repository.find_by_id(
            environment_id
        )

        if environment is None:
            raise EnvironmentNotFoundError(environment_id)

        return environment

    def _require_tenant(self, tenant_id: str) -> TenantModel:
        """Garante que o tenant institucional exista."""

        tenant = self._tenant_repository.find_by_id(tenant_id)

        if tenant is None:
            raise TenantNotFoundError(tenant_id)

        return tenant

    def _require_company_scope(
        self,
        current_user: AuthenticatedUser,
        company: CompanyModel,
    ) -> None:
        """Exige acesso à hierarquia institucional da empresa."""

        environment = self._require_environment(
            company.environment_id
        )
        tenant = self._require_tenant(environment.tenant_id)
        self._authorization_service.require_scope(
            current_user,
            organization_id=tenant.organization_id,
            tenant_id=tenant.id,
            environment_id=environment.id,
        )

    def _require_roles(
        self,
        current_user: AuthenticatedUser,
    ) -> None:
        """Exige um papel permitido para leitura do dashboard."""

        self._authorization_service.require_roles(
            current_user,
            DASHBOARD_READER_ROLES,
        )