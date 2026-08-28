/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Contrato de persistência dos chamados do módulo.
 */

import {
  Ticket,
  TicketCreateInput,
  TicketStatusInput,
  TicketUpdateInput,
} from './ticket';

import {
  TicketFilters,
} from './ticket-filters';

export interface TicketRepository {

  list(
    filters?: TicketFilters,
  ): Promise<readonly Ticket[]>;

  findById(
    id: string,
  ): Promise<Ticket | undefined>;

  create(
    input: TicketCreateInput,
  ): Promise<Ticket>;

  update(
    id: string,
    input: TicketUpdateInput,
  ): Promise<Ticket>;

  updateStatus(
    id: string,
    input: TicketStatusInput,
  ): Promise<Ticket>;

}