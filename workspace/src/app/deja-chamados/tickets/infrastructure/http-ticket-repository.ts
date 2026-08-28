/*
 * Deja Chamados
 *
 * Tickets Infrastructure
 *
 * Repositório HTTP responsável pela integração com a FastAPI.
 */

import {
  HttpClient,
  HttpErrorResponse,
  HttpParams,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  Ticket,
  TicketCreateInput,
  TicketFilters,
  TicketRepository,
  TicketStatus,
  TicketStatusInput,
  TicketPriority,
  TicketUpdateInput,
  TicketValidator,
} from '../domain';

interface TicketResponse {
  id: string;

  organization_id: string;
  tenant_id: string;
  environment_id: string;
  client_id: string;

  title: string;
  description: string;

  status: TicketStatus;
  priority: TicketPriority;

  opened_by_user_id: string;
  assigned_to_user_id: string | null;
  closed_by_user_id: string | null;
  closed_at: string | null;

  created_at: string;
  updated_at: string;
}

interface TicketCreateRequest {
  environment_id: string;
  client_id: string;

  title: string;
  description: string;

  priority: TicketPriority;
  assigned_to_user_id: string | null;
}

interface TicketUpdateRequest {
  title: string;
  description: string;

  priority: TicketPriority;
  assigned_to_user_id: string | null;
}

interface TicketStatusRequest {
  status: TicketStatus;
}

export class HttpTicketRepository implements TicketRepository {

  private readonly validator = new TicketValidator();

  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(
    filters: TicketFilters = {},
  ): Promise<readonly Ticket[]> {
    const response = await firstValueFrom(
      this.http.get<readonly TicketResponse[]>(
        '/api/chamados/tickets',
        {
          params: this.mapFilters(filters),
        },
      ),
    );

    return response.map(ticket => this.mapTicket(ticket));
  }

  async findById(
    id: string,
  ): Promise<Ticket | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<TicketResponse>(
          `/api/chamados/tickets/${id}`,
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

  async create(
    input: TicketCreateInput,
  ): Promise<Ticket> {
    const response = await firstValueFrom(
      this.http.post<TicketResponse>(
        '/api/chamados/tickets',
        this.mapCreateRequest(input),
      ),
    );

    return this.mapTicket(response);
  }

  async update(
    id: string,
    input: TicketUpdateInput,
  ): Promise<Ticket> {
    const response = await firstValueFrom(
      this.http.put<TicketResponse>(
        `/api/chamados/tickets/${id}`,
        this.mapUpdateRequest(input),
      ),
    );

    return this.mapTicket(response);
  }

  async updateStatus(
    id: string,
    input: TicketStatusInput,
  ): Promise<Ticket> {
    const response = await firstValueFrom(
      this.http.patch<TicketResponse>(
        `/api/chamados/tickets/${id}/status`,
        this.mapStatusRequest(input),
      ),
    );

    return this.mapTicket(response);
  }

  private mapFilters(
    filters: TicketFilters,
  ): HttpParams {
    let params = new HttpParams();

    if (filters.organizationId) {
      params = params.set(
        'organization_id',
        filters.organizationId,
      );
    }

    if (filters.tenantId) {
      params = params.set(
        'tenant_id',
        filters.tenantId,
      );
    }

    if (filters.environmentId) {
      params = params.set(
        'environment_id',
        filters.environmentId,
      );
    }

    if (filters.clientId) {
      params = params.set(
        'client_id',
        filters.clientId,
      );
    }

    if (filters.status) {
      params = params.set(
        'status',
        filters.status,
      );
    }

    if (filters.priority) {
      params = params.set(
        'priority',
        filters.priority,
      );
    }

    if (filters.assignedToUserId) {
      params = params.set(
        'assigned_to_user_id',
        filters.assignedToUserId,
      );
    }

    if (filters.search) {
      params = params.set(
        'search',
        filters.search.trim(),
      );
    }

    return params;
  }

  private mapCreateRequest(
    input: TicketCreateInput,
  ): TicketCreateRequest {
    const validatedInput = this.validator.validateCreate(input);

    return {
      environment_id: validatedInput.environmentId,
      client_id: validatedInput.clientId,
      title: validatedInput.title,
      description: validatedInput.description,
      priority: validatedInput.priority,
      assigned_to_user_id: validatedInput.assignedToUserId,
    };
  }

  private mapUpdateRequest(
    input: TicketUpdateInput,
  ): TicketUpdateRequest {
    const validatedInput = this.validator.validateUpdate(input);

    return {
      title: validatedInput.title,
      description: validatedInput.description,
      priority: validatedInput.priority,
      assigned_to_user_id: validatedInput.assignedToUserId,
    };
  }

  private mapStatusRequest(
    input: TicketStatusInput,
  ): TicketStatusRequest {
    return this.validator.validateStatus(input);
  }

  private mapTicket(
    response: TicketResponse,
  ): Ticket {
    return {
      id: response.id,
      organizationId: response.organization_id,
      tenantId: response.tenant_id,
      environmentId: response.environment_id,
      clientId: response.client_id,
      title: response.title,
      description: response.description,
      status: response.status,
      priority: response.priority,
      openedByUserId: response.opened_by_user_id,
      assignedToUserId: response.assigned_to_user_id,
      closedByUserId: response.closed_by_user_id,
      closedAt: response.closed_at,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

}
