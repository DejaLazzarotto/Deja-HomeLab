/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Utilitários de cálculo de SLA dos chamados.
 */

import {
  Ticket,
} from './ticket';

import {
  TICKET_SLA_RULES,
} from './ticket-sla';

export interface TicketSlaInfo {
  dueAt: string;
  isExpired: boolean;
  remainingHours: number;
}

export function calculateTicketSla(
  ticket: Ticket,
): TicketSlaInfo {
  const rule = TICKET_SLA_RULES[ticket.priority];

  const createdAt = new Date(ticket.createdAt);

  const dueDate = new Date(
    createdAt.getTime() +
      rule.hoursToResolve * 60 * 60 * 1000,
  );

  const remainingMs =
    dueDate.getTime() - Date.now();

  const remainingHours = Math.floor(
    remainingMs / (1000 * 60 * 60),
  );

  return {
    dueAt: dueDate.toISOString(),
    isExpired: remainingMs < 0,
    remainingHours,
  };
}