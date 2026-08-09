/*
 * Deja Indicadores
 *
 * Companies Domain
 *
 * Erro utilizado quando já existe uma empresa com o documento informado.
 */

export class CompanyDocumentAlreadyExistsError extends Error {

  constructor(
    readonly document: string,
  ) {
    super(`Company document already exists: ${document}`);

    this.name = 'CompanyDocumentAlreadyExistsError';
  }

}