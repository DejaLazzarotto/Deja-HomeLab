/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Filtros disponíveis para consulta de chamados.
 */

import {
  TicketPriority,
  TicketStatus,
} from './ticket';

export interface TicketFilters {
  organizationId?: string;
  tenantId?: string;
  environmentId?: string;
  clientId?: string;

  status?: TicketStatus;
  priority?: TicketPriority;
  assignedToUserId?: string;

  search?: string;
}