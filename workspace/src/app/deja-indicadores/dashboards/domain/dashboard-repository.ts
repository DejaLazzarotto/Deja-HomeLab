/*
 * Deja Indicadores
 *
 * Dashboards Domain
 *
 * Contrato de acesso à visão gerencial.
 */

import {
  Dashboard,
} from './dashboard';

import {
  DashboardFilters,
} from './dashboard-filters';

export interface DashboardRepository {

  getOverview(
    filters?: DashboardFilters,
  ): Promise<Dashboard>;

}