/*
 * Deja Indicadores
 *
 * Indicators Domain
 *
 * Contrato de persistência dos indicadores.
 */

import {
  Indicator,
} from './indicator';

import {
  IndicatorInput,
} from './indicator-input';

export interface IndicatorRepository {
  list(): Promise<readonly Indicator[]>;

  findById(
    id: string,
  ): Promise<Indicator | undefined>;

  create(
    input: IndicatorInput,
  ): Promise<Indicator>;

  update(
    id: string,
    input: IndicatorInput,
  ): Promise<Indicator>;

  delete(
    id: string,
  ): Promise<void>;
}