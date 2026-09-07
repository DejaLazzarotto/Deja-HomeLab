/*
 * Deja Chamados
 *
 * Queue Board Utils
 *
 * Regras de agrupamento e ordenação da Fila de Chamados.
 */

import {
  Ticket,
  TicketPriority,
  TicketStatus,
} from '../../../tickets';

const PRIORITY_WEIGHT: Readonly<
  Record<TicketPriority, number>
> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
};

export function sortQueueTickets(
  tickets: readonly Ticket[],
  status: TicketStatus,
): readonly Ticket[] {
  return [...tickets]
    .filter(ticket => ticket.status === status)
    .sort((left, right) => {
      if (status === 'closed') {
        return dateValue(right.updatedAt)
          - dateValue(left.updatedAt);
      }

      const priorityDifference =
        PRIORITY_WEIGHT[left.priority]
        - PRIORITY_WEIGHT[right.priority];

      if (priorityDifference !== 0) {
        return priorityDifference;
      }

      return dateValue(left.updatedAt)
        - dateValue(right.updatedAt);
    });
}

function dateValue(
  value: string,
): number {
  return new Date(value).getTime();
}
