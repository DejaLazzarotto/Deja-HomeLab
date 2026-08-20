/*
 * Deja Indicadores
 *
 * Measurements Domain
 *
 * Erro de validação dos dados de uma medição.
 */

export class InvalidMeasurementError extends Error {

  constructor(
    message: string,
  ) {
    super(message);
    this.name = 'InvalidMeasurementError';
  }

}