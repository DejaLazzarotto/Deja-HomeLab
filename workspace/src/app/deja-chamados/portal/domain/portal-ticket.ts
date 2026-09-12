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

export type PortalTimelineEventType =
  | 'created'
  | 'priority_changed'
  | 'assigned_changed'
  | 'updated'
  | 'status_changed';

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

export interface PortalTimelineEvent {
  readonly id: string;
  readonly eventType: PortalTimelineEventType;
  readonly description: string;
  readonly previousValue: string | null;
  readonly newValue: string | null;
  readonly createdAt: string;
}

export interface PortalTicketComment {
  readonly id: string;
  readonly content: string;
  readonly createdBy: string | null;
  readonly createdAt: string;
}

export interface PortalTicketCommentCreate {
  readonly content: string;
}

export interface PortalTicketAttachment {
  readonly id: string;
  readonly originalName: string;
  readonly contentType: string;
  readonly fileSize: number;
  readonly createdBy: string | null;
  readonly createdAt: string;
}
