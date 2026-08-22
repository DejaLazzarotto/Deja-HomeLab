/*
 * Deja Chamados
 *
 * Clients Domain
 *
 * Erro lançado quando um cliente não é encontrado.
 */

export class ClientNotFoundError extends Error {

  constructor(
    id: string,
  ) {
    super(
      `Cliente não encontrado: ${id}.`,
    );

    this.name = 'ClientNotFoundError';
  }

}