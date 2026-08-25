import {
  ModuleKey,
  ModuleManagementRepository,
  Organization,
  OrganizationInput,
  OrganizationModules,
  ModuleCatalogItem,
} from '../domain';

export class ModuleManagementService {

  constructor(
    private readonly repository: ModuleManagementRepository,
  ) {}

  listOrganizations(): Promise<readonly Organization[]> {
    return this.repository.listOrganizations();
  }

  createOrganization(
    input: OrganizationInput,
  ): Promise<Organization> {
    return this.repository.createOrganization(input);
  }

  updateOrganization(
    id: string,
    input: OrganizationInput,
  ): Promise<Organization> {
    return this.repository.updateOrganization(id, input);
  }

  listCatalog(): Promise<readonly ModuleCatalogItem[]> {
    return this.repository.listCatalog();
  }

  getOrganizationModules(
    organizationId: string,
  ): Promise<OrganizationModules> {
    return this.repository.getOrganizationModules(
      organizationId,
    );
  }

  updateOrganizationModules(
    organizationId: string,
    enabledModules: readonly ModuleKey[],
  ): Promise<OrganizationModules> {
    return this.repository.updateOrganizationModules(
      organizationId,
      enabledModules,
    );
  }

}