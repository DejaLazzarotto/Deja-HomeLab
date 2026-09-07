/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Representa um evento do histórico de um chamado.
 */

export interface TicketTimelineEvent {
  id: string;
  ticketId: string;

  eventType: string;
  description: string;

  previousValue: string | null;
  newValue: string | null;

  createdByUserId: string | null;
  createdAt: string;
}
