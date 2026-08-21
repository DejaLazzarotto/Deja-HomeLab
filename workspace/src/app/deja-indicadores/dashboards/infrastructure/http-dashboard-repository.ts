/*
 * Deja Indicadores
 *
 * Dashboards Infrastructure
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
  DashboardRepository,
} from '../domain';

interface DashboardStatusCountResponse {
  readonly status: string;
  readonly count: number;
}

interface DashboardMeasurementResponse {
  readonly id: string;
  readonly reference_date: string;
  readonly actual_value: number | string;
  readonly observation: string | null;
}

interface DashboardIndicatorResponse {
  readonly id: string;
  readonly company_id: string;
  readonly company_trade_name: string;
  readonly name: string;
  readonly unit: string;
  readonly direction: DashboardIndicator['direction'];
  readonly status: DashboardIndicator['status'];
  readonly target_value: number | string;
  readonly current_measurement:
    DashboardMeasurementResponse | null;
  readonly achievement_percentage:
    number | string | null;
  readonly situation: DashboardIndicator['situation'];
  readonly history:
    readonly DashboardMeasurementResponse[];
}

interface DashboardResponse {
  readonly totals: {
    readonly companies: number;
    readonly indicators: number;
    readonly measurements: number;
  };
  readonly companies_by_status:
    readonly DashboardStatusCountResponse[];
  readonly indicators_by_status:
    readonly DashboardStatusCountResponse[];
  readonly indicators:
    readonly DashboardIndicatorResponse[];
}

export class HttpDashboardRepository
implements DashboardRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async getOverview(
    filters: DashboardFilters = {},
  ): Promise<Dashboard> {
    const response = await firstValueFrom(
      this.http.get<DashboardResponse>(
        '/api/dashboards/overview',
        {
          params: this.createParams(filters),
        },
      ),
    );

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

  private mapIndicator(
    response: DashboardIndicatorResponse,
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
    response: DashboardMeasurementResponse,
  ): DashboardMeasurement {
    return {
      id: response.id,
      referenceDate: response.reference_date,
      actualValue: Number(response.actual_value),
      observation: response.observation ?? '',
    };
  }

}