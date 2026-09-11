/*
 * Deja Chamados
 *
 * Tickets Infrastructure
 *
 * Repositório HTTP responsável pelos comentários dos chamados.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  TicketComment,
  TicketCommentCreateInput,
  TicketCommentRepository,
} from '../domain';

interface TicketCommentResponse {
  readonly id: string;
  readonly ticket_id: string;
  readonly content: string;
  readonly visibility: 'public' | 'internal';
  readonly created_by_user_id: string | null;
  readonly created_by: string | null;
  readonly created_at: string;
}

export class HttpTicketCommentRepository
implements TicketCommentRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketComment[]> {
    const response = await firstValueFrom(
      this.http.get<readonly TicketCommentResponse[]>(
        `/api/chamados/tickets/${ticketId}/comments`,
      ),
    );

    return response.map(
      comment => this.mapComment(comment),
    );
  }

  async create(
    ticketId: string,
    input: TicketCommentCreateInput,
  ): Promise<TicketComment> {
    const response = await firstValueFrom(
      this.http.post<TicketCommentResponse>(
        `/api/chamados/tickets/${ticketId}/comments`,
        {
          content: input.content,
          visibility: input.visibility,
        },
      ),
    );

    return this.mapComment(response);
  }

  private mapComment(
    comment: TicketCommentResponse,
  ): TicketComment {
    return {
      id: comment.id,
      ticketId: comment.ticket_id,
      content: comment.content,
      visibility: comment.visibility,
      createdByUserId: comment.created_by_user_id,
      createdBy: comment.created_by,
      createdAt: comment.created_at,
    };
  }

}