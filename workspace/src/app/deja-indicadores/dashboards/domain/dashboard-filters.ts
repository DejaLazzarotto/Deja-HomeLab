/*
 * Deja Indicadores
 *
 * Dashboards Domain
 *
 * Filtros disponíveis para a visão gerencial.
 */

export interface DashboardFilters {
  readonly companyId?: string;
  readonly indicatorId?: string;
  readonly organizationId?: string;
  readonly tenantId?: string;
  readonly environmentId?: string;
  readonly startDate?: string;
  readonly endDate?: string;
}