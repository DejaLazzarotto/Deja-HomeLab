/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Contrato de consulta dos responsáveis elegíveis.
 */

import {
  TicketAssignee,
} from './ticket-assignee';

export interface TicketAssigneeRepository {

  list(
    clientId: string,
  ): Promise<readonly TicketAssignee[]>;

}