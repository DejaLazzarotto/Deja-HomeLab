import {
  Environment,
  EnvironmentInput,
  ModuleCatalogItem,
  ModuleKey,
  ModuleManagementRepository,
  Organization,
  OrganizationInput,
  OrganizationModules,
  Tenant,
  TenantInput,
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

  listTenants(
    organizationId?: string,
  ): Promise<readonly Tenant[]> {
    return this.repository.listTenants(
      organizationId,
    );
  }

  createTenant(
    input: TenantInput,
  ): Promise<Tenant> {
    return this.repository.createTenant(input);
  }

  updateTenant(
    id: string,
    input: TenantInput,
  ): Promise<Tenant> {
    return this.repository.updateTenant(
      id,
      input,
    );
  }

  deleteTenant(
    id: string,
  ): Promise<void> {
    return this.repository.deleteTenant(id);
  }

  listEnvironments(
    tenantId?: string,
  ): Promise<readonly Environment[]> {
    return this.repository.listEnvironments(
      tenantId,
    );
  }

  createEnvironment(
    input: EnvironmentInput,
  ): Promise<Environment> {
    return this.repository.createEnvironment(input);
  }

  updateEnvironment(
    id: string,
    input: EnvironmentInput,
  ): Promise<Environment> {
    return this.repository.updateEnvironment(
      id,
      input,
    );
  }

  deleteEnvironment(
    id: string,
  ): Promise<void> {
    return this.repository.deleteEnvironment(id);
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