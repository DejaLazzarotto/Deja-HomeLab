import {
  ChangeDetectionStrategy,
  Component,
  Input,
  OnInit,
  signal,
} from '@angular/core';

import {
  FormsModule,
} from '@angular/forms';

import {
  Environment,
  EnvironmentInput,
  ModuleKey,
  ModuleManagementService,
  Organization,
  OrganizationInput,
  OrganizationModule,
  OrganizationStatus,
  Tenant,
  TenantEnvironmentStatus,
  TenantInput,
} from '../../index';

@Component({
  selector: 'deja-organization-management',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './organization-management.html',
  styleUrl: './organization-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrganizationManagementComponent
implements OnInit {

  @Input({
    required: true,
  })
  service!: ModuleManagementService;

  readonly organizations =
    signal<readonly Organization[]>([]);

  readonly selectedOrganization =
    signal<Organization | null>(null);

  readonly modules =
    signal<readonly OrganizationModule[]>([]);

  readonly enabledModules =
    signal<readonly ModuleKey[]>([]);

  readonly tenants =
    signal<readonly Tenant[]>([]);

  readonly selectedTenant =
    signal<Tenant | null>(null);

  readonly environments =
    signal<readonly Environment[]>([]);

  readonly loading = signal(false);

  readonly loadingModules = signal(false);

  readonly loadingTenants = signal(false);

  readonly loadingEnvironments = signal(false);

  readonly saving = signal(false);

  readonly savingModules = signal(false);

  readonly savingTenant = signal(false);

  readonly savingEnvironment = signal(false);

  readonly formVisible = signal(false);

  readonly tenantFormVisible = signal(false);

  readonly environmentFormVisible = signal(false);

  readonly editingOrganizationId =
    signal<string | null>(null);

  readonly editingTenantId =
    signal<string | null>(null);

  readonly editingEnvironmentId =
    signal<string | null>(null);

  readonly errorMessage =
    signal<string | null>(null);

  readonly operationMessage =
    signal<string | null>(null);

  form: OrganizationInput = this.emptyForm();

  tenantForm: TenantInput =
    this.emptyTenantForm();

  environmentForm: EnvironmentInput =
    this.emptyEnvironmentForm();

  ngOnInit(): void {
    void this.refresh();
  }

  async refresh(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const organizations =
        await this.service.listOrganizations();

      this.organizations.set(organizations);

      const selected = this.selectedOrganization();

      if (selected) {
        const updated = organizations.find(
          organization => organization.id === selected.id,
        );

        if (updated) {
          this.selectedOrganization.set(updated);
        }
      }
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar as organizações.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openCreate(): void {
    this.editingOrganizationId.set(null);
    this.form = this.emptyForm();
    this.formVisible.set(true);
    this.operationMessage.set(null);
    this.errorMessage.set(null);
  }

  openEdit(
    organization: Organization,
  ): void {
    this.editingOrganizationId.set(organization.id);
    this.form = {
      code: organization.code,
      name: organization.name,
      status: organization.status,
    };
    this.formVisible.set(true);
    this.operationMessage.set(null);
    this.errorMessage.set(null);
  }

  closeForm(): void {
    this.formVisible.set(false);
    this.editingOrganizationId.set(null);
  }

  async saveOrganization(): Promise<void> {
    if (!this.form.code.trim() || !this.form.name.trim()) {
      this.errorMessage.set(
        'Informe o código e o nome da organização.',
      );
      return;
    }

    this.saving.set(true);
    this.errorMessage.set(null);
    this.operationMessage.set(null);

    try {
      const editingId = this.editingOrganizationId();

      const saved = editingId
        ? await this.service.updateOrganization(
            editingId,
            this.form,
          )
        : await this.service.createOrganization(
            this.form,
          );

      this.operationMessage.set(
        editingId
          ? 'Organização atualizada com sucesso.'
          : 'Organização cadastrada com sucesso.',
      );

      this.closeForm();

      await this.refresh();
      await this.selectOrganization(saved);
    } catch {
      this.errorMessage.set(
        'Não foi possível salvar a organização.',
      );
    } finally {
      this.saving.set(false);
    }
  }

  async selectOrganization(
    organization: Organization,
  ): Promise<void> {
    this.selectedOrganization.set(organization);
    this.selectedTenant.set(null);
    this.environments.set([]);

    this.closeTenantForm();
    this.closeEnvironmentForm();

    this.errorMessage.set(null);

    await Promise.all([
      this.loadModules(organization.id),
      this.loadTenants(organization.id),
    ]);
  }

  isModuleEnabled(
    moduleKey: ModuleKey,
  ): boolean {
    return this.enabledModules().includes(moduleKey);
  }

  setModuleEnabled(
    moduleKey: ModuleKey,
    enabled: boolean,
  ): void {
    const current = this.enabledModules();

    this.enabledModules.set(
      enabled
        ? [...new Set([...current, moduleKey])]
        : current.filter(key => key !== moduleKey),
    );
  }

  async saveModules(): Promise<void> {
    const organization = this.selectedOrganization();

    if (!organization) {
      return;
    }

    this.savingModules.set(true);
    this.errorMessage.set(null);
    this.operationMessage.set(null);

    try {
      const response =
        await this.service.updateOrganizationModules(
          organization.id,
          this.enabledModules(),
        );

      this.modules.set(response.modules);

      this.enabledModules.set(
        response.modules
          .filter(module => module.enabled)
          .map(module => module.key),
      );

      this.operationMessage.set(
        'Aplicativos contratados atualizados com sucesso.',
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível salvar os aplicativos contratados.',
      );
    } finally {
      this.savingModules.set(false);
    }
  }

  openCreateTenant(): void {
    const organization = this.selectedOrganization();

    if (!organization) {
      return;
    }

    this.editingTenantId.set(null);

    this.tenantForm = {
      ...this.emptyTenantForm(),
      organizationId: organization.id,
    };

    this.tenantFormVisible.set(true);
    this.operationMessage.set(null);
    this.errorMessage.set(null);
  }

  openEditTenant(
    tenant: Tenant,
  ): void {
    this.editingTenantId.set(tenant.id);

    this.tenantForm = {
      organizationId: tenant.organizationId,
      name: tenant.name,
      status: tenant.status,
    };

    this.tenantFormVisible.set(true);
    this.operationMessage.set(null);
    this.errorMessage.set(null);
  }

  closeTenantForm(): void {
    this.tenantFormVisible.set(false);
    this.editingTenantId.set(null);
  }

  async saveTenant(): Promise<void> {
    const organization = this.selectedOrganization();

    if (!organization) {
      return;
    }

    if (!this.tenantForm.name.trim()) {
      this.errorMessage.set(
        'Informe o nome do tenant.',
      );
      return;
    }

    this.savingTenant.set(true);
    this.errorMessage.set(null);
    this.operationMessage.set(null);

    try {
      const editingId = this.editingTenantId();

      const input: TenantInput = {
        ...this.tenantForm,
        organizationId: organization.id,
      };

      const saved = editingId
        ? await this.service.updateTenant(
            editingId,
            input,
          )
        : await this.service.createTenant(input);

      this.operationMessage.set(
        editingId
          ? 'Tenant atualizado com sucesso.'
          : 'Tenant cadastrado com sucesso.',
      );

      this.closeTenantForm();

      await this.loadTenants(organization.id);
      await this.selectTenant(saved);
    } catch {
      this.errorMessage.set(
        'Não foi possível salvar o tenant.',
      );
    } finally {
      this.savingTenant.set(false);
    }
  }

  async deleteTenant(
    tenant: Tenant,
  ): Promise<void> {
    const organization = this.selectedOrganization();

    if (!organization) {
      return;
    }

    this.errorMessage.set(null);
    this.operationMessage.set(null);

    try {
      await this.service.deleteTenant(tenant.id);

      if (this.selectedTenant()?.id === tenant.id) {
        this.selectedTenant.set(null);
        this.environments.set([]);
      }

      await this.loadTenants(organization.id);

      this.operationMessage.set(
        'Tenant excluído com sucesso.',
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível excluir o tenant.',
      );
    }
  }

  async selectTenant(
    tenant: Tenant,
  ): Promise<void> {
    this.selectedTenant.set(tenant);

    this.closeEnvironmentForm();

    await this.loadEnvironments(tenant.id);
  }

  openCreateEnvironment(): void {
    const tenant = this.selectedTenant();

    if (!tenant) {
      return;
    }

    this.editingEnvironmentId.set(null);

    this.environmentForm = {
      ...this.emptyEnvironmentForm(),
      tenantId: tenant.id,
    };

    this.environmentFormVisible.set(true);
    this.operationMessage.set(null);
    this.errorMessage.set(null);
  }

  openEditEnvironment(
    environment: Environment,
  ): void {
    this.editingEnvironmentId.set(environment.id);

    this.environmentForm = {
      tenantId: environment.tenantId,
      name: environment.name,
      status: environment.status,
    };

    this.environmentFormVisible.set(true);
    this.operationMessage.set(null);
    this.errorMessage.set(null);
  }

  closeEnvironmentForm(): void {
    this.environmentFormVisible.set(false);
    this.editingEnvironmentId.set(null);
  }

  async saveEnvironment(): Promise<void> {
    const tenant = this.selectedTenant();

    if (!tenant) {
      return;
    }

    if (!this.environmentForm.name.trim()) {
      this.errorMessage.set(
        'Informe o nome do ambiente.',
      );
      return;
    }

    this.savingEnvironment.set(true);
    this.errorMessage.set(null);
    this.operationMessage.set(null);

    try {
      const editingId = this.editingEnvironmentId();

      const input: EnvironmentInput = {
        ...this.environmentForm,
        tenantId: tenant.id,
      };

      editingId
        ? await this.service.updateEnvironment(
            editingId,
            input,
          )
        : await this.service.createEnvironment(input);

      this.operationMessage.set(
        editingId
          ? 'Ambiente atualizado com sucesso.'
          : 'Ambiente cadastrado com sucesso.',
      );

      this.closeEnvironmentForm();

      await this.loadEnvironments(tenant.id);
    } catch {
      this.errorMessage.set(
        'Não foi possível salvar o ambiente.',
      );
    } finally {
      this.savingEnvironment.set(false);
    }
  }

  async deleteEnvironment(
    environment: Environment,
  ): Promise<void> {
    const tenant = this.selectedTenant();

    if (!tenant) {
      return;
    }

    this.errorMessage.set(null);
    this.operationMessage.set(null);

    try {
      await this.service.deleteEnvironment(
        environment.id,
      );

      await this.loadEnvironments(tenant.id);

      this.operationMessage.set(
        'Ambiente excluído com sucesso.',
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível excluir o ambiente.',
      );
    }
  }

  statusLabel(
    status: OrganizationStatus | TenantEnvironmentStatus,
  ): string {
    const labels: Record<
      OrganizationStatus | TenantEnvironmentStatus,
      string
    > = {
      provisioning: 'Provisionando',
      active: 'Ativa',
      inactive: 'Inativa',
    };

    return labels[status];
  }

  private async loadModules(
    organizationId: string,
  ): Promise<void> {
    this.loadingModules.set(true);

    try {
      const response =
        await this.service.getOrganizationModules(
          organizationId,
        );

      this.modules.set(response.modules);

      this.enabledModules.set(
        response.modules
          .filter(module => module.enabled)
          .map(module => module.key),
      );
    } catch {
      this.modules.set([]);
      this.enabledModules.set([]);

      this.errorMessage.set(
        'Não foi possível carregar os aplicativos da organização.',
      );
    } finally {
      this.loadingModules.set(false);
    }
  }

  private async loadTenants(
    organizationId: string,
  ): Promise<void> {
    this.loadingTenants.set(true);

    try {
      const tenants =
        await this.service.listTenants(
          organizationId,
        );

      this.tenants.set(tenants);

      const selected = this.selectedTenant();

      if (selected) {
        const updated = tenants.find(
          tenant => tenant.id === selected.id,
        );

        if (updated) {
          this.selectedTenant.set(updated);
        }
      }
    } catch {
      this.tenants.set([]);

      this.errorMessage.set(
        'Não foi possível carregar os tenants da organização.',
      );
    } finally {
      this.loadingTenants.set(false);
    }
  }

  private async loadEnvironments(
    tenantId: string,
  ): Promise<void> {
    this.loadingEnvironments.set(true);

    try {
      const environments =
        await this.service.listEnvironments(
          tenantId,
        );

      this.environments.set(environments);
    } catch {
      this.environments.set([]);

      this.errorMessage.set(
        'Não foi possível carregar os ambientes do tenant.',
      );
    } finally {
      this.loadingEnvironments.set(false);
    }
  }

  private emptyForm(): OrganizationInput {
    return {
      code: '',
      name: '',
      status: 'provisioning',
    };
  }

  private emptyTenantForm(): TenantInput {
    return {
      organizationId: '',
      name: '',
      status: 'provisioning',
    };
  }

  private emptyEnvironmentForm(): EnvironmentInput {
    return {
      tenantId: '',
      name: '',
      status: 'provisioning',
    };
  }

}