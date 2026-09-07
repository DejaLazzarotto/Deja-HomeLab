/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Regras de prazo de atendimento por prioridade.
 */

import {
  TicketPriority,
} from './ticket';

export interface TicketSlaRule {
  priority: TicketPriority;
  hoursToResolve: number;
  label: string;
}

export const TICKET_SLA_RULES: Readonly<
  Record<TicketPriority, TicketSlaRule>
> = {
  low: {
    priority: 'low',
    hoursToResolve: 72,
    label: '72h',
  },
  medium: {
    priority: 'medium',
    hoursToResolve: 48,
    label: '48h',
  },
  high: {
    priority: 'high',
    hoursToResolve: 24,
    label: '24h',
  },
  critical: {
    priority: 'critical',
    hoursToResolve: 4,
    label: '4h',
  },
};