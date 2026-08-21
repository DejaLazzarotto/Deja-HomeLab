/*
 * Deja Indicadores
 *
 * Reports Domain
 *
 * Contrato de acesso aos relatórios gerenciais.
 */

import {
  DashboardFilters,
} from '../../dashboards/domain';

import {
  ManagementReport,
} from './management-report';

export interface ReportRepository {

  getManagementReport(
    filters?: DashboardFilters,
  ): Promise<ManagementReport>;

}