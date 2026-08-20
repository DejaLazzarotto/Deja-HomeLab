/*
 * Deja Indicadores
 *
 * Indicators Domain
 *
 * Dados utilizados na criação e atualização de indicadores.
 */

import {
  IndicatorDirection,
  IndicatorStatus,
} from './indicator';

export interface IndicatorInput {
  readonly companyId: string;
  readonly name: string;
  readonly description: string;
  readonly unit: string;
  readonly direction: IndicatorDirection;
  readonly targetValue: number;
  readonly status: IndicatorStatus;
}