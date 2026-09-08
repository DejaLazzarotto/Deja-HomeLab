export type PortalTicketStatus =
  | 'open'
  | 'in_progress'
  | 'pending'
  | 'closed';

export type PortalTicketPriority =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical';

export interface PortalTicket {
  readonly id: string;

  readonly title: string;
  readonly description: string;

  readonly status: PortalTicketStatus;
  readonly priority: PortalTicketPriority;

  readonly assignedToUserName: string | null;
  readonly closedAt: string | null;

  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface PortalTicketCreate {
  readonly title: string;
  readonly description: string;
}