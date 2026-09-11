/*
 * Deja Chamados
 *
 * Tickets Infrastructure
 *
 * Repositório HTTP responsável pela consulta do histórico dos chamados.
 */

import {
  HttpClient,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  TicketTimelineEvent,
  TicketTimelineRepository,
} from '../domain';

interface TicketTimelineResponse {
  readonly id: string;
  readonly ticket_id: string;

  readonly event_type: string;
  readonly description: string;

  readonly previous_value: string | null;
  readonly new_value: string | null;

  readonly previous_display_value: string | null;
  readonly new_display_value: string | null;

  readonly created_by_user_id: string | null;
  readonly created_at: string;
}

export class HttpTicketTimelineRepository
implements TicketTimelineRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async listByTicketId(
    ticketId: string,
  ): Promise<readonly TicketTimelineEvent[]> {
    const response = await firstValueFrom(
      this.http.get<readonly TicketTimelineResponse[]>(
        `/api/chamados/tickets/${ticketId}/timeline`,
      ),
    );

    return response.map(event => ({
      id: event.id,
      ticketId: event.ticket_id,
      eventType: event.event_type,
      description: event.description,
      previousValue: event.previous_value,
      newValue: event.new_value,
      previousDisplayValue: event.previous_display_value,
      newDisplayValue: event.new_display_value,
      createdByUserId: event.created_by_user_id,
      createdAt: event.created_at,
    }));
  }

}