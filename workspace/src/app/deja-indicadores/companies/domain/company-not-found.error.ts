/*
 * Deja Indicadores
 *
 * Companies Domain
 *
 * Erro utilizado quando uma empresa não é encontrada.
 */

export class CompanyNotFoundError extends Error {

  constructor(
    readonly companyId: string,
  ) {
    super(`Company not found: ${companyId}`);

    this.name = 'CompanyNotFoundError';
  }

}