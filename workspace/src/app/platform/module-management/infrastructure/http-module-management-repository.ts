import {
  HttpClient,
} from '@angular/common/http';

import {
  firstValueFrom,
} from 'rxjs';

import {
  ModuleCatalogItem,
  ModuleKey,
  ModuleManagementRepository,
  Organization,
  OrganizationInput,
  OrganizationModule,
  OrganizationModules,
} from '../domain';

interface OrganizationResponse {
  readonly id: string;
  readonly code: string;
  readonly name: string;
  readonly status: Organization['status'];
  readonly created_at: string;
  readonly updated_at: string;
}

interface ModuleResponse {
  readonly key: ModuleKey;
  readonly name: string;
  readonly description: string | null;
  readonly display_order: number;
  readonly created_at: string;
  readonly updated_at: string;
}

interface OrganizationModuleResponse {
  readonly key: ModuleKey;
  readonly name: string;
  readonly description: string | null;
  readonly display_order: number;
  readonly enabled: boolean;
}

interface OrganizationModulesResponse {
  readonly organization_id: string;
  readonly modules: readonly OrganizationModuleResponse[];
}

export class HttpModuleManagementRepository
implements ModuleManagementRepository {

  constructor(
    private readonly http: HttpClient,
  ) {}

  async listOrganizations(): Promise<readonly Organization[]> {
    const response = await firstValueFrom(
      this.http.get<readonly OrganizationResponse[]>(
        '/api/v1/organizations',
      ),
    );

    return response.map(item => this.mapOrganization(item));
  }

  async createOrganization(
    input: OrganizationInput,
  ): Promise<Organization> {
    const response = await firstValueFrom(
      this.http.post<OrganizationResponse>(
        '/api/v1/organizations',
        this.mapOrganizationRequest(input),
      ),
    );

    return this.mapOrganization(response);
  }

  async updateOrganization(
    id: string,
    input: OrganizationInput,
  ): Promise<Organization> {
    const response = await firstValueFrom(
      this.http.put<OrganizationResponse>(
        `/api/v1/organizations/${id}`,
        this.mapOrganizationRequest(input),
      ),
    );

    return this.mapOrganization(response);
  }

  async listCatalog(): Promise<readonly ModuleCatalogItem[]> {
    const response = await firstValueFrom(
      this.http.get<readonly ModuleResponse[]>(
        '/api/v1/modules',
      ),
    );

    return response.map(item => ({
      key: item.key,
      name: item.name,
      description: item.description,
      displayOrder: item.display_order,
      createdAt: item.created_at,
      updatedAt: item.updated_at,
    }));
  }

  async getOrganizationModules(
    organizationId: string,
  ): Promise<OrganizationModules> {
    const response = await firstValueFrom(
      this.http.get<OrganizationModulesResponse>(
        `/api/v1/organizations/${organizationId}/modules`,
      ),
    );

    return this.mapOrganizationModules(response);
  }

  async updateOrganizationModules(
    organizationId: string,
    enabledModules: readonly ModuleKey[],
  ): Promise<OrganizationModules> {
    const response = await firstValueFrom(
      this.http.put<OrganizationModulesResponse>(
        `/api/v1/organizations/${organizationId}/modules`,
        {
          enabled_modules: enabledModules,
        },
      ),
    );

    return this.mapOrganizationModules(response);
  }

  private mapOrganizationRequest(
    input: OrganizationInput,
  ): Record<string, string> {
    return {
      code: input.code.trim().toUpperCase(),
      name: input.name.trim(),
      status: input.status,
    };
  }

  private mapOrganization(
    response: OrganizationResponse,
  ): Organization {
    return {
      id: response.id,
      code: response.code,
      name: response.name,
      status: response.status,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

  private mapOrganizationModules(
    response: OrganizationModulesResponse,
  ): OrganizationModules {
    return {
      organizationId: response.organization_id,
      modules: response.modules.map(
        (item): OrganizationModule => ({
          key: item.key,
          name: item.name,
          description: item.description,
          displayOrder: item.display_order,
          enabled: item.enabled,
        }),
      ),
    };
  }

}