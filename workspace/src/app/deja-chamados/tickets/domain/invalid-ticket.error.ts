/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Erro lançado quando os dados de um chamado são inválidos.
 */

export class InvalidTicketError extends Error {

  constructor(
    message: string,
  ) {
    super(message);

    this.name = 'InvalidTicketError';
  }

}