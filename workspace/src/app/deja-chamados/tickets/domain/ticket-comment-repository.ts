/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Contrato de acesso aos comentários dos chamados.
 */

import {
  TicketComment,
  TicketCommentCreateInput,
} from './ticket-comment';

export interface TicketCommentRepository {
  listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketComment[]>;

  create(
    ticketId: string,
    input: TicketCommentCreateInput,
  ): Promise<TicketComment>;
}