/*
 * Deja Chamados
 *
 * Tickets Application
 *
 * Serviço responsável por consultar o histórico dos chamados.
 */

import {
  TicketTimelineEvent,
  TicketTimelineRepository,
} from '../domain';

export class TicketTimelineService {

  constructor(
    private readonly repository: TicketTimelineRepository,
  ) {}

  listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketTimelineEvent[]> {
    return this.repository.listByTicketId(ticketId);
  }

}
