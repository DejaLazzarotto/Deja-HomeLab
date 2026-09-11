/*
 * Deja Chamados
 *
 * Tickets Application
 *
 * Serviço responsável por coordenar os comentários dos chamados.
 */

import {
  TicketComment,
  TicketCommentCreateInput,
  TicketCommentRepository,
} from '../domain';

export class TicketCommentService {

  constructor(
    private readonly repository: TicketCommentRepository,
  ) {}

  listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketComment[]> {
    return this.repository.listByTicketId(
      ticketId,
    );
  }

  create(
    ticketId: string,
    input: TicketCommentCreateInput,
  ): Promise<TicketComment> {
    return this.repository.create(
      ticketId,
      input,
    );
  }

}