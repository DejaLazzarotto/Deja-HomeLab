/*
 * Deja Indicadores
 *
 * Users Infrastructure
 *
 * Repositório HTTP responsável pela integração com a FastAPI.
 */

import {
  ModuleKey,
} from '../../module-management/domain/module-key';

import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';

import { firstValueFrom } from 'rxjs';

import {
  User,
  UserFilters,
  UserInput,
  UserModuleAccesses,
  UserModuleAccessSelection,
  UserRepository,
  UserValidator,
} from '../domain';

interface UserResponse {
  readonly id: string;
  readonly organization_id: string | null;
  readonly tenant_id: string | null;
  readonly environment_id: string | null;
  readonly name: string;
  readonly email: string;
  readonly role: User['role'];
  readonly status: User['status'];
  readonly created_at: string;
  readonly updated_at: string;
}

interface UserRequest {
  readonly organization_id: string | null;
  readonly tenant_id: string | null;
  readonly environment_id: string | null;
  readonly name: string;
  readonly email: string;
  readonly role: User['role'];
  readonly status: User['status'];
}

interface UserModuleAccessResponse {
  readonly key: ModuleKey;
  readonly name: string;
  readonly description: string | null;
  readonly display_order: number;
  readonly organization_enabled: boolean;
  readonly has_access: boolean;
  readonly role: 'manager' | 'analyst' | 'viewer' | null;
}

interface UserModuleAccessesResponse {
  readonly user_id: string;
  readonly modules: readonly UserModuleAccessResponse[];
}

export class HttpUserRepository implements UserRepository {
  private readonly validator = new UserValidator();

  constructor(private readonly http: HttpClient) {}

  async list(filters: UserFilters = {}): Promise<readonly User[]> {
    let params = new HttpParams();

    if (filters.organizationId) {
      params = params.set('organization_id', filters.organizationId);
    }

    if (filters.tenantId) {
      params = params.set('tenant_id', filters.tenantId);
    }

    if (filters.environmentId) {
      params = params.set('environment_id', filters.environmentId);
    }

    if (filters.status) {
      params = params.set('user_status', filters.status);
    }

    const response = await firstValueFrom(
      this.http.get<readonly UserResponse[]>('/api/v1/users', {
        params,
      }),
    );

    return response.map((user) => this.mapUser(user));
  }

  async findById(id: string): Promise<User | undefined> {
    try {
      const response = await firstValueFrom(this.http.get<UserResponse>(`/api/v1/users/${id}`));

      return this.mapUser(response);
    } catch (error: unknown) {
      if (error instanceof HttpErrorResponse && error.status === 404) {
        return undefined;
      }

      throw error;
    }
  }

  async create(input: UserInput): Promise<User> {
    const response = await firstValueFrom(
      this.http.post<UserResponse>('/api/v1/users', this.mapRequest(input)),
    );

    return this.mapUser(response);
  }

  async update(id: string, input: UserInput): Promise<User> {
    const response = await firstValueFrom(
      this.http.put<UserResponse>(`/api/v1/users/${id}`, this.mapRequest(input)),
    );

    return this.mapUser(response);
  }

  async setPassword(id: string, password: string): Promise<User> {
    const response = await firstValueFrom(
      this.http.put<UserResponse>(`/api/v1/users/${id}/password`, {
        password,
      }),
    );

    return this.mapUser(response);
  }

  async getModuleAccesses(id: string): Promise<UserModuleAccesses> {
    const response = await firstValueFrom(
      this.http.get<UserModuleAccessesResponse>(`/api/v1/users/${id}/modules`),
    );

    return this.mapModuleAccesses(response);
  }

  async updateModuleAccesses(
    id: string,
    modules: readonly UserModuleAccessSelection[],
  ): Promise<UserModuleAccesses> {
    const response = await firstValueFrom(
      this.http.put<UserModuleAccessesResponse>(`/api/v1/users/${id}/modules`, {
        modules: modules.map((module) => ({
          module_key: module.moduleKey,
          role: module.role,
        })),
      }),
    );

    return this.mapModuleAccesses(response);
  }

  private mapRequest(input: UserInput): UserRequest {
    const validatedInput = this.validator.validate(input);

    return {
      organization_id: validatedInput.organizationId,
      tenant_id: validatedInput.tenantId,
      environment_id: validatedInput.environmentId,
      name: validatedInput.name,
      email: validatedInput.email,
      role: validatedInput.role,
      status: validatedInput.status,
    };
  }

  private mapUser(response: UserResponse): User {
    return {
      id: response.id,
      organizationId: response.organization_id,
      tenantId: response.tenant_id,
      environmentId: response.environment_id,
      name: response.name,
      email: response.email,
      role: response.role,
      status: response.status,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

  private mapModuleAccesses(response: UserModuleAccessesResponse): UserModuleAccesses {
    return {
      userId: response.user_id,
      modules: response.modules.map((module) => ({
        key: module.key,
        name: module.name,
        description: module.description,
        displayOrder: module.display_order,
        organizationEnabled: module.organization_enabled,
        hasAccess: module.has_access,
        role: module.role,
      })),
    };
  }
}
