/*
 * Deja Indicadores
 *
 * Indicators Domain
 *
 * Modelo institucional de indicador operacional.
 */

export type IndicatorDirection =
  | 'higher_is_better'
  | 'lower_is_better';

export type IndicatorStatus =
  | 'active'
  | 'inactive';

export interface Indicator {
  readonly id: string;
  readonly companyId: string;
  readonly name: string;
  readonly description: string;
  readonly unit: string;
  readonly direction: IndicatorDirection;
  readonly targetValue: number;
  readonly status: IndicatorStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
}