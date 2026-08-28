/*
 * Deja Chamados
 *
 * Tickets Infrastructure
 *
 * Repositório HTTP dos responsáveis elegíveis.
 */

import {
  HttpClient,
  HttpParams,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  TicketAssignee,
  TicketAssigneeRepository,
  TicketAssigneeRole,
} from '../domain';

interface TicketAssigneeResponse {
  readonly id: string;
  readonly name: string;
  readonly email: string;
  readonly role: TicketAssigneeRole;
}

export class HttpTicketAssigneeRepository
implements TicketAssigneeRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(
    clientId: string,
  ): Promise<readonly TicketAssignee[]> {
    const params = new HttpParams().set(
      'client_id',
      clientId,
    );

    const response = await firstValueFrom(
      this.http.get<readonly TicketAssigneeResponse[]>(
        '/api/chamados/tickets/assignees',
        {
          params,
        },
      ),
    );

    return response.map(assignee => ({
      id: assignee.id,
      name: assignee.name,
      email: assignee.email,
      role: assignee.role,
    }));
  }

}