/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Erro lançado quando um chamado não é encontrado.
 */

export class TicketNotFoundError extends Error {

  constructor(
    readonly ticketId: string,
  ) {
    super(`Chamado não encontrado: ${ticketId}`);

    this.name = 'TicketNotFoundError';
  }

}