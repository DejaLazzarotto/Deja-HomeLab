/*
 * Deja Chamados
 *
 * Clients Domain
 *
 * Erro lançado quando os dados de um cliente são inválidos.
 */

export class InvalidClientError extends Error {

  constructor(
    message = 'Os dados do cliente são inválidos.',
  ) {
    super(message);

    this.name = 'InvalidClientError';
  }

}