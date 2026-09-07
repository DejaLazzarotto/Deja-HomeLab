/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Contrato de acesso ao histórico dos chamados.
 */

import {
  TicketTimelineEvent,
} from './ticket-timeline';

export interface TicketTimelineRepository {
  listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketTimelineEvent[]>;
}
