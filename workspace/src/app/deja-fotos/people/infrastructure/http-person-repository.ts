/*
 * Deja Fotos
 *
 * Repositório HTTP de Pessoas.
 */

import {
  HttpClient,
  HttpParams,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  Person,
  PersonFilters,
  PersonInput,
  PersonPage,
  PersonRepository,
} from '../domain/person';

interface PersonResponse {
  readonly id: string;
  readonly organization_id: string;
  readonly tenant_id: string;
  readonly environment_id: string;
  readonly name: string;
  readonly description: string | null;
  readonly active: boolean;
  readonly avatar_content_type: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

interface PersonPageResponse {
  readonly items: readonly PersonResponse[];
  readonly page: number;
  readonly page_size: number;
  readonly total: number;
  readonly total_pages: number;
}

export class HttpPersonRepository
  implements PersonRepository {
  constructor(
    private readonly http: HttpClient,
  ) {}

  async list(
    filters: PersonFilters = {},
  ): Promise<PersonPage> {
    let params = new HttpParams()
      .set(
        'page',
        String(filters.page ?? 1),
      )
      .set(
        'page_size',
        String(filters.pageSize ?? 50),
      );

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
    if (filters.name) {
      params = params.set(
        'name',
        filters.name,
      );
    }

    const response = await firstValueFrom(
      this.http.get<PersonPageResponse>(
        '/api/fotos/people',
        { params },
      ),
    );

    return {
      items: response.items.map(
        item => this.mapPerson(item),
      ),
      page: response.page,
      pageSize: response.page_size,
      total: response.total,
      totalPages: response.total_pages,
    };
  }

  async create(
    input: PersonInput,
  ): Promise<Person> {
    const response = await firstValueFrom(
      this.http.post<PersonResponse>(
        '/api/fotos/people',
        this.mapInput(input),
      ),
    );

    return this.mapPerson(response);
  }

  async update(
    id: string,
    input: PersonInput,
  ): Promise<Person> {
    const response = await firstValueFrom(
      this.http.put<PersonResponse>(
        `/api/fotos/people/${id}`,
        this.mapInput(input),
      ),
    );

    return this.mapPerson(response);
  }

  async delete(id: string): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        `/api/fotos/people/${id}`,
      ),
    );
  }

  loadAvatar(id: string): Promise<Blob> {
    return firstValueFrom(
      this.http.get(
        `/api/fotos/people/${id}/avatar`,
        { responseType: 'blob' },
      ),
    );
  }

  async uploadAvatar(
    id: string,
    file: File,
  ): Promise<Person> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await firstValueFrom(
      this.http.put<PersonResponse>(
        `/api/fotos/people/${id}/avatar`,
        formData,
      ),
    );

    return this.mapPerson(response);
  }

  async removeAvatar(
    id: string,
  ): Promise<Person> {
    const response = await firstValueFrom(
      this.http.delete<PersonResponse>(
        `/api/fotos/people/${id}/avatar`,
      ),
    );

    return this.mapPerson(response);
  }

  async linkMedia(
    personId: string,
    mediaId: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.post<void>(
        `/api/fotos/people/${personId}/media`,
        { media_id: mediaId },
      ),
    );
  }

  async unlinkMedia(
    personId: string,
    mediaId: string,
  ): Promise<void> {
    await firstValueFrom(
      this.http.delete<void>(
        (
          `/api/fotos/people/${personId}`
          + `/media/${mediaId}`
        ),
      ),
    );
  }

  private mapInput(
    input: PersonInput,
  ): object {
    return {
      environment_id: input.environmentId,
      name: input.name,
      description: input.description,
      active: input.active,
    };
  }

  private mapPerson(
    response: PersonResponse,
  ): Person {
    return {
      id: response.id,
      organizationId: response.organization_id,
      tenantId: response.tenant_id,
      environmentId: response.environment_id,
      name: response.name,
      description: response.description,
      active: response.active,
      avatarContentType: response.avatar_content_type,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }
}