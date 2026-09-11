/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Representa um comentário associado a um chamado.
 */

export type TicketCommentVisibility =
  | 'public'
  | 'internal';

export interface TicketComment {
  readonly id: string;
  readonly ticketId: string;
  readonly content: string;
  readonly visibility: TicketCommentVisibility;
  readonly createdByUserId: string | null;
  readonly createdBy: string | null;
  readonly createdAt: string;
}

export interface TicketCommentCreateInput {
  readonly content: string;
  readonly visibility: TicketCommentVisibility;
}