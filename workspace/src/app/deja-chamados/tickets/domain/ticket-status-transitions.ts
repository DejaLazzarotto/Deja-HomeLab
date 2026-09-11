/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Define as transições de status permitidas para os chamados.
 */

import {
  TicketStatus,
} from './ticket';

export const TICKET_STATUS_TRANSITIONS: Readonly<
  Record<TicketStatus, readonly TicketStatus[]>
> = {
  open: [
    'in_progress',
    'pending',
    'closed',
  ],
  in_progress: [
    'open',
    'pending',
    'closed',
  ],
  pending: [
    'open',
    'in_progress',
    'closed',
  ],
  closed: [
    'open',
  ],
};