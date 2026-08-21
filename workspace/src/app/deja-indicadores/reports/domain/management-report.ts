/*
 * Deja Indicadores
 *
 * Reports Domain
 *
 * Modelo do relatório gerencial operacional.
 */

import {
  Dashboard,
} from '../../dashboards/domain';

export interface ManagementReportFilters {
  readonly companyId: string | null;
  readonly indicatorId: string | null;
  readonly organizationId: string | null;
  readonly tenantId: string | null;
  readonly environmentId: string | null;
  readonly startDate: string | null;
  readonly endDate: string | null;
}

export interface ManagementReport {
  readonly title: string;
  readonly generatedAt: string;
  readonly filters: ManagementReportFilters;
  readonly overview: Dashboard;
}