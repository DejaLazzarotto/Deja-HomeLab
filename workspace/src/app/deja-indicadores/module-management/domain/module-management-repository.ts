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

export interface ModuleManagementRepository {

  listOrganizations(): Promise<readonly Organization[]>;

  createOrganization(
    input: OrganizationInput,
  ): Promise<Organization>;

  updateOrganization(
    id: string,
    input: OrganizationInput,
  ): Promise<Organization>;

  listCatalog(): Promise<readonly ModuleCatalogItem[]>;

  getOrganizationModules(
    organizationId: string,
  ): Promise<OrganizationModules>;

  updateOrganizationModules(
    organizationId: string,
    enabledModules: readonly ModuleKey[],
  ): Promise<OrganizationModules>;

}