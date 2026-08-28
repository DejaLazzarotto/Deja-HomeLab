/*
 * Deja Chamados
 *
 * Tickets Application
 *
 * Serviço responsável por consultar usuários elegíveis para atribuição.
 */

import {
  TicketAssignee,
  TicketAssigneeRepository,
} from '../domain';

export class TicketAssigneeService {

  constructor(
    private readonly repository: TicketAssigneeRepository,
  ) {}

  list(
    clientId: string,
  ): Promise<readonly TicketAssignee[]> {
    return this.repository.list(clientId);
  }

}