/*
 * Deja Indicadores
 *
 * Indicators Domain
 *
 * Erro lançado quando um indicador não é encontrado.
 */

export class IndicatorNotFoundError extends Error {

  constructor(
    id: string,
  ) {
    super(`Indicador não encontrado: ${id}`);
    this.name = 'IndicatorNotFoundError';
  }

}