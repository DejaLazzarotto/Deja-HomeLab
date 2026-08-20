/*
 * Deja Indicadores
 *
 * Measurements Domain
 *
 * Filtros disponíveis para consulta de medições.
 */

export interface MeasurementFilters {
  readonly companyId?: string;
  readonly indicatorId?: string;
  readonly startDate?: string;
  readonly endDate?: string;
}