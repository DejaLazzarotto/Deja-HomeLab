/*
 * Deja Indicadores
 *
 * Measurements Domain
 *
 * Erro utilizado quando uma medição não é encontrada.
 */

export class MeasurementNotFoundError extends Error {

  constructor(
    id: string,
  ) {
    super(`Medição não encontrada: ${id}`);
    this.name = 'MeasurementNotFoundError';
  }

}