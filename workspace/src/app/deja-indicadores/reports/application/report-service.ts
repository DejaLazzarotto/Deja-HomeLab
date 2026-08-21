/*
 * Deja Indicadores
 *
 * Reports Application
 *
 * Serviço de aplicação dos relatórios gerenciais.
 */

import {
  DashboardFilters,
} from '../../dashboards/domain';

import {
  ManagementReport,
  ReportRepository,
} from '../domain';

export class ReportService {

  constructor(
    private readonly repository:
      ReportRepository,
  ) {}

  getManagementReport(
    filters: DashboardFilters = {},
  ): Promise<ManagementReport> {
    return this.repository.getManagementReport(filters);
  }

}