/*
 * Deja Fotos
 *
 * Album HTTP Repository
 *
 * Integra o domínio de álbuns com a API FastAPI.
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
  Album,
  AlbumFilters,
  AlbumInput,
  AlbumRepository,
} from '../domain';

interface AlbumResponse {
  readonly id: string;

  readonly organization_id: string;
  readonly tenant_id: string;
  readonly environment_id: string;

  readonly name: string;
  readonly description: string | null;
  readonly active: boolean;

  readonly created_at: string;
  readonly updated_at: string;
}

interface AlbumRequest {
  readonly environment_id: string;
  readonly name: string;
  readonly description: string | null;
  readonly active: boolean;
}

export class HttpAlbumRepository implements AlbumRepository {
  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(
    filters: AlbumFilters = {},
  ): Promise<readonly Album[]> {
    const response = await firstValueFrom(
      this.http.get<readonly AlbumResponse[]>(
        '/api/fotos/albums',
        {
          params: this.mapFilters(filters),
        },
      ),
    );

    return response.map(album => this.mapAlbum(album));
  }

  async findById(
    id: string,
  ): Promise<Album | undefined> {
    try {
      const response = await firstValueFrom(
        this.http.get<AlbumResponse>(
          `/api/fotos/albums/${id}`,
        ),
      );

      return this.mapAlbum(response);
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
    input: AlbumInput,
  ): Promise<Album> {
    const response = await firstValueFrom(
      this.http.post<AlbumResponse>(
        '/api/fotos/albums',
        this.mapRequest(input),
      ),
    );

    return this.mapAlbum(response);
  }

  async update(
    id: string,
    input: AlbumInput,
  ): Promise<Album> {
    const response = await firstValueFrom(
      this.http.put<AlbumResponse>(
        `/api/fotos/albums/${id}`,
        this.mapRequest(input),
      ),
    );

    return this.mapAlbum(response);
  }

  async delete(
    id: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/fotos/albums/${id}`,
      ),
    );
  }

  private mapFilters(
    filters: AlbumFilters,
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

    if (filters.active !== undefined) {
      params = params.set(
        'active',
        String(filters.active),
      );
    }

    return params;
  }

  private mapRequest(
    input: AlbumInput,
  ): AlbumRequest {
    return {
      environment_id: input.environmentId,
      name: input.name,
      description: input.description,
      active: input.active,
    };
  }

  private mapAlbum(
    response: AlbumResponse,
  ): Album {
    return {
      id: response.id,
      organizationId: response.organization_id,
      tenantId: response.tenant_id,
      environmentId: response.environment_id,
      name: response.name,
      description: response.description,
      active: response.active,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }
}