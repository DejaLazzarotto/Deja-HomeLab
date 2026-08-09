/*
 * Deja Indicadores
 *
 * Companies Domain
 *
 * Erro utilizado quando os dados informados para uma empresa são inválidos.
 */

export class InvalidCompanyError extends Error {

  constructor(
    readonly field: string,
    message: string,
  ) {
    super(message);

    this.name = 'InvalidCompanyError';
  }

}