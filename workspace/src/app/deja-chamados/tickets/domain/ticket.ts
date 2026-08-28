/*
 * Deja Chamados
 *
 * Tickets Domain
 *
 * Representa um chamado operacional dentro do escopo da plataforma.
 */

export type TicketStatus =
  | 'open'
  | 'in_progress'
  | 'pending'
  | 'closed';

export type TicketPriority =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical';

export interface Ticket {
  id: string;

  organizationId: string;
  tenantId: string;
  environmentId: string;
  clientId: string;

  title: string;
  description: string;

  status: TicketStatus;
  priority: TicketPriority;

  openedByUserId: string;
  assignedToUserId: string | null;
  closedByUserId: string | null;
  closedAt: string | null;

  createdAt: string;
  updatedAt: string;
}

export interface TicketCreateInput {
  environmentId: string;
  clientId: string;

  title: string;
  description: string;

  priority: TicketPriority;
  assignedToUserId: string | null;
}

export interface TicketUpdateInput {
  title: string;
  description: string;

  priority: TicketPriority;
  assignedToUserId: string | null;
}

export interface TicketStatusInput {
  status: TicketStatus;
}