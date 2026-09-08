import {
  HttpClient,
  HttpErrorResponse,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  ClientUserLink,
  ClientUserLinkCreate,
  ClientUserLinkUpdate,
} from '../domain/client-user-link';

interface ClientUserLinkResponse {
  readonly id: string;
  readonly user_id: string;
  readonly client_id: string;
  readonly created_at: string;
}

interface ClientUserLinkCreateRequest {
  readonly user_id: string;
  readonly client_id: string;
}

interface ClientUserLinkUpdateRequest {
  readonly client_id: string;
}

export class HttpClientUserLinkRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async findByUserId(
    userId: string,
  ): Promise<ClientUserLink | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<ClientUserLinkResponse>(
          `/api/chamados/client-users/${userId}`,
        ),
      );

      return this.mapLink(response);
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
    input: ClientUserLinkCreate,
  ): Promise<ClientUserLink> {
    const response = await firstValueFrom(
      this.http.post<ClientUserLinkResponse>(
        '/api/chamados/client-users',
        this.mapCreateRequest(input),
      ),
    );

    return this.mapLink(response);
  }

  async update(
    userId: string,
    input: ClientUserLinkUpdate,
  ): Promise<ClientUserLink> {
    const response = await firstValueFrom(
      this.http.put<ClientUserLinkResponse>(
        `/api/chamados/client-users/${userId}`,
        this.mapUpdateRequest(input),
      ),
    );

    return this.mapLink(response);
  }

  async delete(
    userId: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/chamados/client-users/${userId}`,
      ),
    );
  }

  private mapCreateRequest(
    input: ClientUserLinkCreate,
  ): ClientUserLinkCreateRequest {
    return {
      user_id: input.userId,
      client_id: input.clientId,
    };
  }

  private mapUpdateRequest(
    input: ClientUserLinkUpdate,
  ): ClientUserLinkUpdateRequest {
    return {
      client_id: input.clientId,
    };
  }

  private mapLink(
    response: ClientUserLinkResponse,
  ): ClientUserLink {
    return {
      id: response.id,
      userId: response.user_id,
      clientId: response.client_id,
      createdAt: response.created_at,
    };
  }
}