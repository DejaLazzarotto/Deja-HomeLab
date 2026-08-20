/*
 * Deja Indicadores
 *
 * Indicators Application
 *
 * Serviço de aplicação das operações de indicadores.
 */

import {
  Indicator,
  IndicatorInput,
  IndicatorNotFoundError,
  IndicatorRepository,
} from '../domain';

export class IndicatorService {

  constructor(
    private readonly repository: IndicatorRepository,
  ) {}

  list(): Promise<readonly Indicator[]> {
    return this.repository.list();
  }

  async findById(
    id: string,
  ): Promise<Indicator> {
    const indicator = await this.repository.findById(id);

    if (!indicator) {
      throw new IndicatorNotFoundError(id);
    }

    return indicator;
  }

  create(
    input: IndicatorInput,
  ): Promise<Indicator> {
    return this.repository.create(input);
  }

  update(
    id: string,
    input: IndicatorInput,
  ): Promise<Indicator> {
    return this.repository.update(id, input);
  }

  delete(
    id: string,
  ): Promise<void> {
    return this.repository.delete(id);
  }

}