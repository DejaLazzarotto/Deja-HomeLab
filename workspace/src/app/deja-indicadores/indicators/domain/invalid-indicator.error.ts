/*
 * Deja Indicadores
 *
 * Indicators Domain
 *
 * Erro lançado quando os dados do indicador são inválidos.
 */

export class InvalidIndicatorError extends Error {

  constructor(
    message: string,
  ) {
    super(message);
    this.name = 'InvalidIndicatorError';
  }

}