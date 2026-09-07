/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Rótulos de apresentação associados aos estados
 * e prioridades dos chamados.
 */

import {
  TicketPriority,
  TicketStatus,
} from './ticket';

export const TICKET_STATUS_LABELS: Readonly<
  Record<TicketStatus, string>
> = {
  open: 'Aberto',
  in_progress: 'Em Atendimento',
  pending: 'Pendente',
  closed: 'Encerrado',
};

export const TICKET_PRIORITY_LABELS: Readonly<
  Record<TicketPriority, string>
> = {
  low: 'Baixa',
  medium: 'Média',
  high: 'Alta',
  critical: 'Crítica',
};