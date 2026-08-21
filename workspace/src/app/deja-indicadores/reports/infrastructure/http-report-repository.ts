/*
 * Deja Indicadores
 *
 * Reports Infrastructure
 *
 * Repositório HTTP responsável pela integração com a FastAPI.
 */

import {
  HttpClient,
  HttpParams,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  Dashboard,
  DashboardFilters,
  DashboardIndicator,
  DashboardMeasurement,
} from '../../dashboards/domain';

import {
  ManagementReport,
  ReportRepository,
} from '../domain';

interface StatusCountResponse {
  readonly status: string;
  readonly count: number;
}

interface MeasurementResponse {
  readonly id: string;
  readonly reference_date: string;
  readonly actual_value: number | string;
  readonly observation: string | null;
}

interface IndicatorResponse {
  readonly id: string;
  readonly company_id: string;
  readonly company_trade_name: string;
  readonly name: string;
  readonly unit: string;
  readonly direction: DashboardIndicator['direction'];
  readonly status: DashboardIndicator['status'];
  readonly target_value: number | string;
  readonly current_measurement:
    MeasurementResponse | null;
  readonly achievement_percentage:
    number | string | null;
  readonly situation: DashboardIndicator['situation'];
  readonly history: readonly MeasurementResponse[];
}

interface OverviewResponse {
  readonly totals: {
    readonly companies: number;
    readonly indicators: number;
    readonly measurements: number;
  };
  readonly companies_by_status:
    readonly StatusCountResponse[];
  readonly indicators_by_status:
    readonly StatusCountResponse[];
  readonly indicators: readonly IndicatorResponse[];
}

interface ManagementReportResponse {
  readonly title: string;
  readonly generated_at: string;
  readonly filters: {
    readonly company_id: string | null;
    readonly indicator_id: string | null;
    readonly organization_id: string | null;
    readonly tenant_id: string | null;
    readonly environment_id: string | null;
    readonly start_date: string | null;
    readonly end_date: string | null;
  };
  readonly overview: OverviewResponse;
}

export class HttpReportRepository
implements ReportRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async getManagementReport(
    filters: DashboardFilters = {},
  ): Promise<ManagementReport> {
    const response = await firstValueFrom(
      this.http.get<ManagementReportResponse>(
        '/api/reports/management',
        {
          params: this.createParams(filters),
        },
      ),
    );

    return {
      title: response.title,
      generatedAt: response.generated_at,
      filters: {
        companyId: response.filters.company_id,
        indicatorId: response.filters.indicator_id,
        organizationId:
          response.filters.organization_id,
        tenantId: response.filters.tenant_id,
        environmentId:
          response.filters.environment_id,
        startDate: response.filters.start_date,
        endDate: response.filters.end_date,
      },
      overview: this.mapOverview(response.overview),
    };
  }

  private createParams(
    filters: DashboardFilters,
  ): HttpParams {
    let params = new HttpParams();

    const values = {
      company_id: filters.companyId,
      indicator_id: filters.indicatorId,
      organization_id: filters.organizationId,
      tenant_id: filters.tenantId,
      environment_id: filters.environmentId,
      start_date: filters.startDate,
      end_date: filters.endDate,
    };

    for (const [name, value] of Object.entries(values)) {
      if (value) {
        params = params.set(name, value);
      }
    }

    return params;
  }

  private mapOverview(
    response: OverviewResponse,
  ): Dashboard {
    return {
      totals: {
        companies: response.totals.companies,
        indicators: response.totals.indicators,
        measurements: response.totals.measurements,
      },
      companiesByStatus:
        response.companies_by_status.map(item => ({
          status: item.status,
          count: item.count,
        })),
      indicatorsByStatus:
        response.indicators_by_status.map(item => ({
          status: item.status,
          count: item.count,
        })),
      indicators:
        response.indicators.map(
          indicator => this.mapIndicator(indicator),
        ),
    };
  }

  private mapIndicator(
    response: IndicatorResponse,
  ): DashboardIndicator {
    return {
      id: response.id,
      companyId: response.company_id,
      companyTradeName:
        response.company_trade_name,
      name: response.name,
      unit: response.unit,
      direction: response.direction,
      status: response.status,
      targetValue: Number(response.target_value),
      currentMeasurement:
        response.current_measurement
          ? this.mapMeasurement(
              response.current_measurement,
            )
          : null,
      achievementPercentage:
        response.achievement_percentage === null
          ? null
          : Number(
              response.achievement_percentage,
            ),
      situation: response.situation,
      history: response.history.map(
        measurement =>
          this.mapMeasurement(measurement),
      ),
    };
  }

  private mapMeasurement(
    response: MeasurementResponse,
  ): DashboardMeasurement {
    return {
      id: response.id,
      referenceDate: response.reference_date,
      actualValue: Number(response.actual_value),
      observation: response.observation ?? '',
    };
  }

}