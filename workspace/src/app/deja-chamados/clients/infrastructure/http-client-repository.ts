/*
 * Deja Chamados
 *
 * Clients Infrastructure
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
  Client,
  ClientFilters,
  ClientInput,
  ClientRepository,
  ClientValidator,
} from '../domain';

interface ClientResponse {
  id: string;

  organization_id: string;
  tenant_id: string;
  environment_id: string;

  company_name: string;
  fantasy_name: string;
  document: string;

  contact_name: string;

  phone: string;
  whatsapp: string;
  email: string;

  city: string;
  state: string;

  notes: string;

  active: boolean;

  created_at: string;
  updated_at: string;

  total_tickets: number;
}

interface ClientRequest {
  environment_id: string;

  company_name: string;
  fantasy_name: string;
  document: string;

  contact_name: string;

  phone: string;
  whatsapp: string;
  email: string;

  city: string;
  state: string;

  notes: string;

  active: boolean;
}

export class HttpClientRepository implements ClientRepository {

  private readonly validator = new ClientValidator();

  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(
    filters: ClientFilters = {},
  ): Promise<readonly Client[]> {
    const response = await firstValueFrom(
      this.http.get<readonly ClientResponse[]>(
        '/api/chamados/clients',
        {
          params: this.mapFilters(filters),
        },
      ),
    );

    return response.map(client => this.mapClient(client));
  }

  async findById(
    id: string,
  ): Promise<Client | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<ClientResponse>(
          `/api/chamados/clients/${id}`,
        ),
      );

      return this.mapClient(response);
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
    input: ClientInput,
  ): Promise<Client> {
    const response = await firstValueFrom(
      this.http.post<ClientResponse>(
        '/api/chamados/clients',
        this.mapRequest(input),
      ),
    );

    return this.mapClient(response);
  }

  async update(
    id: string,
    input: ClientInput,
  ): Promise<Client> {
    const response = await firstValueFrom(
      this.http.put<ClientResponse>(
        `/api/chamados/clients/${id}`,
        this.mapRequest(input),
      ),
    );

    return this.mapClient(response);
  }

  async delete(
    id: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/chamados/clients/${id}`,
      ),
    );
  }

  private mapFilters(
    filters: ClientFilters,
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

    if (filters.search) {
      params = params.set(
        'search',
        filters.search.trim(),
      );
    }

    if (filters.active !== undefined) {
      params = params.set(
        'active',
        String(filters.active),
      );
    }

    return params;
  }

  private mapRequest(
    input: ClientInput,
  ): ClientRequest {
    const validatedInput = this.validator.validate(input);

    return {
      environment_id: validatedInput.environmentId,
      company_name: validatedInput.companyName,
      fantasy_name: validatedInput.fantasyName,
      document: validatedInput.document,
      contact_name: validatedInput.contactName,
      phone: validatedInput.phone,
      whatsapp: validatedInput.whatsapp,
      email: validatedInput.email,
      city: validatedInput.city,
      state: validatedInput.state,
      notes: validatedInput.notes,
      active: validatedInput.active,
    };
  }

  private mapClient(
    response: ClientResponse,
  ): Client {
    return {
      id: response.id,
      organizationId: response.organization_id,
      tenantId: response.tenant_id,
      environmentId: response.environment_id,
      companyName: response.company_name,
      fantasyName: response.fantasy_name,
      document: response.document,
      contactName: response.contact_name,
      phone: response.phone,
      whatsapp: response.whatsapp,
      email: response.email,
      city: response.city,
      state: response.state,
      notes: response.notes,
      active: response.active,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
      totalTickets: response.total_tickets,
    };
  }

}