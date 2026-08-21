/*
 * Deja Indicadores
 *
 * Dashboards Domain
 *
 * Modelos da visão gerencial dos indicadores.
 */

export type DashboardIndicatorDirection =
  | 'higher_is_better'
  | 'lower_is_better';

export type DashboardIndicatorStatus =
  | 'active'
  | 'inactive';

export type DashboardSituation =
  | 'on_target'
  | 'below_target'
  | 'above_target'
  | 'no_data';

export interface DashboardStatusCount {
  readonly status: string;
  readonly count: number;
}

export interface DashboardMeasurement {
  readonly id: string;
  readonly referenceDate: string;
  readonly actualValue: number;
  readonly observation: string;
}

export interface DashboardIndicator {
  readonly id: string;
  readonly companyId: string;
  readonly companyTradeName: string;
  readonly name: string;
  readonly unit: string;
  readonly direction: DashboardIndicatorDirection;
  readonly status: DashboardIndicatorStatus;
  readonly targetValue: number;
  readonly currentMeasurement: DashboardMeasurement | null;
  readonly achievementPercentage: number | null;
  readonly situation: DashboardSituation;
  readonly history: readonly DashboardMeasurement[];
}

export interface DashboardTotals {
  readonly companies: number;
  readonly indicators: number;
  readonly measurements: number;
}

export interface Dashboard {
  readonly totals: DashboardTotals;
  readonly companiesByStatus: readonly DashboardStatusCount[];
  readonly indicatorsByStatus: readonly DashboardStatusCount[];
  readonly indicators: readonly DashboardIndicator[];
}