from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from deja_indicadores_api.companies.models import CompanyStatus
from deja_indicadores_api.indicators.models import (
    IndicatorDirection,
    IndicatorStatus,
)


class DashboardSituation(StrEnum):
    """Situações possíveis de um indicador perante sua meta."""

    ON_TARGET = "on_target"
    BELOW_TARGET = "below_target"
    ABOVE_TARGET = "above_target"
    NO_DATA = "no_data"


class DashboardStatusCount(BaseModel):
    """Quantidade de registros associada a um status."""

    status: str
    count: int


class DashboardMeasurement(BaseModel):
    """Medição apresentada no histórico gerencial."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    reference_date: date
    actual_value: Decimal
    observation: str | None


class DashboardIndicator(BaseModel):
    """Visão gerencial de um indicador."""

    id: str
    company_id: str
    company_trade_name: str
    name: str
    unit: str
    direction: IndicatorDirection
    status: IndicatorStatus
    target_value: Decimal
    current_measurement: DashboardMeasurement | None
    achievement_percentage: Decimal | None
    situation: DashboardSituation
    history: list[DashboardMeasurement]


class DashboardTotals(BaseModel):
    """Totais consolidados do dashboard."""

    companies: int
    indicators: int
    measurements: int


class DashboardOverviewResponse(BaseModel):
    """Resposta consolidada do dashboard gerencial."""

    totals: DashboardTotals
    companies_by_status: list[DashboardStatusCount]
    indicators_by_status: list[DashboardStatusCount]
    indicators: list[DashboardIndicator]