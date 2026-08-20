/*
 * Deja Indicadores
 *
 * Measurements Application
 *
 * Serviço de aplicação das operações de medições.
 */

import {
  Measurement,
  MeasurementFilters,
  MeasurementInput,
  MeasurementNotFoundError,
  MeasurementRepository,
} from '../domain';

export class MeasurementService {

  constructor(
    private readonly repository: MeasurementRepository,
  ) {}

  list(
    filters?: MeasurementFilters,
  ): Promise<readonly Measurement[]> {
    return this.repository.list(filters);
  }

  async findById(
    id: string,
  ): Promise<Measurement> {
    const measurement =
      await this.repository.findById(id);

    if (!measurement) {
      throw new MeasurementNotFoundError(id);
    }

    return measurement;
  }

  create(
    input: MeasurementInput,
  ): Promise<Measurement> {
    return this.repository.create(input);
  }

  update(
    id: string,
    input: MeasurementInput,
  ): Promise<Measurement> {
    return this.repository.update(id, input);
  }

  delete(
    id: string,
  ): Promise<void> {
    return this.repository.delete(id);
  }

}