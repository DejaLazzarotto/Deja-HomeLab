import {
  HttpClient,
  HttpErrorResponse,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  PortalTicket,
  PortalTicketCreate,
  PortalTicketPriority,
  PortalTicketStatus,
  PortalTimelineEvent,
  PortalTimelineEventType,
} from '../domain/portal-ticket';

interface PortalTicketResponse {
  id: string;

  title: string;
  description: string;

  status: PortalTicketStatus;
  priority: PortalTicketPriority;

  assigned_to_user_name: string | null;
  closed_at: string | null;

  created_at: string;
  updated_at: string;
}

interface PortalTicketCreateRequest {
  title: string;
  description: string;
}

interface PortalTimelineEventResponse {
  id: string;
  event_type: PortalTimelineEventType;
  description: string;

  previous_value: string | null;
  new_value: string | null;

  created_at: string;
}

export class HttpPortalTicketRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(): Promise<readonly PortalTicket[]> {
    const response = await firstValueFrom(
      this.http.get<readonly PortalTicketResponse[]>(
        '/api/chamados/portal/tickets',
      ),
    );

    return response.map(
      ticket => this.mapTicket(ticket),
    );
  }

  async findById(
    id: string,
  ): Promise<PortalTicket | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<PortalTicketResponse>(
          `/api/chamados/portal/tickets/${id}`,
        ),
      );

      return this.mapTicket(response);
    } catch (error: unknown) {
      if (
        error instanceof HttpErrorResponse
        && error.status === 404
      ) {
        return undefined;
      }

      throw error;
    }
  }

  async listTimeline(
    ticketId: string,
  ): Promise<readonly PortalTimelineEvent[]> {
    const response = await firstValueFrom(
      this.http.get<readonly PortalTimelineEventResponse[]>(
        `/api/chamados/portal/tickets/${ticketId}/timeline`,
      ),
    );

    return response.map(
      event => this.mapTimelineEvent(event),
    );
  }

  async create(
    input: PortalTicketCreate,
  ): Promise<PortalTicket> {
    const response = await firstValueFrom(
      this.http.post<PortalTicketResponse>(
        '/api/chamados/portal/tickets',
        this.mapCreateRequest(input),
      ),
    );

    return this.mapTicket(response);
  }

  private mapCreateRequest(
    input: PortalTicketCreate,
  ): PortalTicketCreateRequest {
    return {
      title: input.title,
      description: input.description,
    };
  }

  private mapTicket(
    response: PortalTicketResponse,
  ): PortalTicket {
    return {
      id: response.id,

      title: response.title,
      description: response.description,

      status: response.status,
      priority: response.priority,

      assignedToUserName:
        response.assigned_to_user_name,

      closedAt: response.closed_at,

      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

  private mapTimelineEvent(
    response: PortalTimelineEventResponse,
  ): PortalTimelineEvent {
    return {
      id: response.id,
      eventType: response.event_type,
      description: response.description,

      previousValue: response.previous_value,
      newValue: response.new_value,

      createdAt: response.created_at,
    };
  }
}