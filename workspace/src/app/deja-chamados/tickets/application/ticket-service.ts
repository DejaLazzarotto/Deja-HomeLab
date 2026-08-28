/*
 * Deja Chamados
 *
 * Tickets Application
 *
 * Serviço responsável por coordenar as operações dos chamados.
 */

import {
  Ticket,
  TicketCreateInput,
  TicketFilters,
  TicketNotFoundError,
  TicketRepository,
  TicketStatusInput,
  TicketUpdateInput,
} from '../domain';

export class TicketService {

  constructor(
    private readonly repository: TicketRepository,
  ) {}

  list(
    filters?: TicketFilters,
  ): Promise<readonly Ticket[]> {
    return this.repository.list(filters);
  }

  async findById(
    id: string,
  ): Promise<Ticket> {
    const ticket = await this.repository.findById(id);

    if (!ticket) {
      throw new TicketNotFoundError(id);
    }

    return ticket;
  }

  create(
    input: TicketCreateInput,
  ): Promise<Ticket> {
    return this.repository.create(input);
  }

  update(
    id: string,
    input: TicketUpdateInput,
  ): Promise<Ticket> {
    return this.repository.update(id, input);
  }

  updateStatus(
    id: string,
    input: TicketStatusInput,
  ): Promise<Ticket> {
    return this.repository.updateStatus(
      id,
      input,
    );
  }

}