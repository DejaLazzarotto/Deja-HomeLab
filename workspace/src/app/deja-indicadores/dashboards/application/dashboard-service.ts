/*
 * Deja Indicadores
 *
 * Dashboards Application
 *
 * Serviço de aplicação da visão gerencial.
 */

import {
  Dashboard,
  DashboardFilters,
  DashboardRepository,
} from '../domain';

export class DashboardService {

  constructor(
    private readonly repository:
      DashboardRepository,
  ) {}

  getOverview(
    filters: DashboardFilters = {},
  ): Promise<Dashboard> {
    return this.repository.getOverview(filters);
  }

}