import {
  ModuleKey,
} from './module-key';

import {
  Organization,
} from './organization';

import {
  OrganizationInput,
} from './organization-input';

import {
  ModuleCatalogItem,
  OrganizationModules,
} from './organization-modules';

import {
  Environment,
  EnvironmentInput,
  Tenant,
  TenantInput,
} from './tenant-environment';

export interface ModuleManagementRepository {

  listOrganizations(): Promise<readonly Organization[]>;

  createOrganization(
    input: OrganizationInput,
  ): Promise<Organization>;

  updateOrganization(
    id: string,
    input: OrganizationInput,
  ): Promise<Organization>;

  listTenants(
    organizationId?: string,
  ): Promise<readonly Tenant[]>;

  createTenant(
    input: TenantInput,
  ): Promise<Tenant>;

  updateTenant(
    id: string,
    input: TenantInput,
  ): Promise<Tenant>;

  deleteTenant(
    id: string,
  ): Promise<void>;

  listEnvironments(
    tenantId?: string,
  ): Promise<readonly Environment[]>;

  createEnvironment(
    input: EnvironmentInput,
  ): Promise<Environment>;

  updateEnvironment(
    id: string,
    input: EnvironmentInput,
  ): Promise<Environment>;

  deleteEnvironment(
    id: string,
  ): Promise<void>;

  listCatalog(): Promise<readonly ModuleCatalogItem[]>;

  getOrganizationModules(
    organizationId: string,
  ): Promise<OrganizationModules>;

  updateOrganizationModules(
    organizationId: string,
    enabledModules: readonly ModuleKey[],
  ): Promise<OrganizationModules>;

}