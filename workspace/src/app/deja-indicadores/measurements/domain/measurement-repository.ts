/*
 * Deja Indicadores
 *
 * Measurements Domain
 *
 * Contrato de persistência das medições.
 */

import {
  Measurement,
} from './measurement';

import {
  MeasurementFilters,
} from './measurement-filters';

import {
  MeasurementInput,
} from './measurement-input';

export interface MeasurementRepository {

  list(
    filters?: MeasurementFilters,
  ): Promise<readonly Measurement[]>;

  findById(
    id: string,
  ): Promise<Measurement | undefined>;

  create(
    input: MeasurementInput,
  ): Promise<Measurement>;

  update(
    id: string,
    input: MeasurementInput,
  ): Promise<Measurement>;

  delete(
    id: string,
  ): Promise<void>;

}