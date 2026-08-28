/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Representa um usuário elegível para receber chamados.
 */

export type TicketAssigneeRole =
  | 'organization_admin'
  | 'tenant_admin'
  | 'manager'
  | 'analyst';

export interface TicketAssignee {
  readonly id: string;
  readonly name: string;
  readonly email: string;
  readonly role: TicketAssigneeRole;
}