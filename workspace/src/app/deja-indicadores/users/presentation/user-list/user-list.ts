/*
 * Deja Indicadores
 *
 * Users Presentation
 *
 * Componente responsável pela administração de usuários.
 */

import {
  HttpErrorResponse,
} from '@angular/common/http';

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
  UserRole,
} from '../../../authentication/domain/authenticated-user';

import {
  User,
  UserInput,
  UserService,
  UserStatus,
} from '../../index';

export interface UserOrganizationOption {
  readonly id: string;
  readonly name: string;
}

export interface UserTenantOption {
  readonly id: string;
  readonly organizationId: string;
  readonly name: string;
}

export interface UserEnvironmentOption {
  readonly id: string;
  readonly tenantId: string;
  readonly name: string;
}

interface UserRoleOption {
  readonly value: UserRole;
  readonly label: string;
}

@Component({
  selector: 'deja-user-list',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './user-list.html',
  styleUrl: './user-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserListComponent implements OnInit {

  @Input({
    required: true,
  })
  service!: UserService;

  @Input({
    required: true,
  })
  currentUserRole!: UserRole;

  @Input()
  organizations: readonly UserOrganizationOption[] = [];

  @Input()
  tenants: readonly UserTenantOption[] = [];

  @Input()
  environments: readonly UserEnvironmentOption[] = [];

  @Input()
  defaultOrganizationId: string | null = null;

  @Input()
  defaultTenantId: string | null = null;

  @Input()
  defaultEnvironmentId: string | null = null;

  readonly users = signal<readonly User[]>([]);

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly savingPassword = signal(false);

  readonly formVisible = signal(false);

  readonly passwordFormVisible = signal(false);

  readonly editingUserId = signal<string | null>(null);

  readonly passwordUser = signal<User | null>(null);

  readonly errorMessage = signal<string | null>(null);

  readonly operationMessage = signal<string | null>(null);

  readonly operationError = signal<string | null>(null);

  filterOrganizationId: string | null = null;

  filterTenantId: string | null = null;

  filterEnvironmentId: string | null = null;

  filterStatus: UserStatus | null = null;

  form: UserInput = this.createEmptyInput();

  password = '';

  passwordConfirmation = '';

  private readonly allRoleOptions:
  readonly UserRoleOption[] = [
    {
      value: 'platform_admin',
      label: 'Administrador da plataforma',
    },
    {
      value: 'organization_admin',
      label: 'Administrador da organização',
    },
    {
      value: 'tenant_admin',
      label: 'Administrador do tenant',
    },
    {
      value: 'manager',
      label: 'Gestor',
    },
    {
      value: 'analyst',
      label: 'Analista',
    },
    {
      value: 'viewer',
      label: 'Visualizador',
    },
  ];

  ngOnInit(): void {
    void this.refresh();
  }

  get roleOptions(): readonly UserRoleOption[] {
    if (this.currentUserRole === 'platform_admin') {
      return this.allRoleOptions;
    }

    if (this.currentUserRole === 'organization_admin') {
      return this.allRoleOptions.filter(
        option => option.value !== 'platform_admin',
      );
    }

    return this.allRoleOptions.filter(
      option => [
        'tenant_admin',
        'manager',
        'analyst',
        'viewer',
      ].includes(option.value),
    );
  }

  get formTenants(): readonly UserTenantOption[] {
    if (!this.form.organizationId) {
      return [];
    }

    return this.tenants.filter(
      tenant =>
        tenant.organizationId === this.form.organizationId,
    );
  }

  get formEnvironments(): readonly UserEnvironmentOption[] {
    if (!this.form.tenantId) {
      return [];
    }

    return this.environments.filter(
      environment =>
        environment.tenantId === this.form.tenantId,
    );
  }

  get filterTenants(): readonly UserTenantOption[] {
    if (!this.filterOrganizationId) {
      return this.tenants;
    }

    return this.tenants.filter(
      tenant =>
        tenant.organizationId === this.filterOrganizationId,
    );
  }

  get filterEnvironments(): readonly UserEnvironmentOption[] {
    if (!this.filterTenantId) {
      return this.filterOrganizationId
        ? this.environments.filter(environment =>
            this.filterTenants.some(
              tenant => tenant.id === environment.tenantId,
            ),
          )
        : this.environments;
    }

    return this.environments.filter(
      environment =>
        environment.tenantId === this.filterTenantId,
    );
  }

  async refresh(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      this.users.set(
        await this.service.list({
          organizationId: this.filterOrganizationId,
          tenantId: this.filterTenantId,
          environmentId: this.filterEnvironmentId,
          status: this.filterStatus,
        }),
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar os usuários.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  applyFilters(): void {
    void this.refresh();
  }

  clearFilters(): void {
    this.filterOrganizationId = null;
    this.filterTenantId = null;
    this.filterEnvironmentId = null;
    this.filterStatus = null;

    void this.refresh();
  }

  onFilterOrganizationChange(): void {
    if (
      this.filterTenantId
      && !this.filterTenants.some(
        tenant => tenant.id === this.filterTenantId,
      )
    ) {
      this.filterTenantId = null;
    }

    this.onFilterTenantChange();
  }

  onFilterTenantChange(): void {
    if (
      this.filterEnvironmentId
      && !this.filterEnvironments.some(
        environment =>
          environment.id === this.filterEnvironmentId,
      )
    ) {
      this.filterEnvironmentId = null;
    }
  }

  openCreate(): void {
    this.editingUserId.set(null);
    this.operationError.set(null);
    this.operationMessage.set(null);

    this.form = this.createEmptyInput();

    this.password = '';
    this.passwordConfirmation = '';
    this.formVisible.set(true);
    this.passwordFormVisible.set(false);
  }

  openEdit(
    user: User,
  ): void {
    this.editingUserId.set(user.id);
    this.operationError.set(null);
    this.operationMessage.set(null);

    this.form = {
      organizationId: user.organizationId,
      tenantId: user.tenantId,
      environmentId: user.environmentId,
      name: user.name,
      email: user.email,
      role: user.role,
      status: user.status,
    };

    this.password = '';
    this.passwordConfirmation = '';
    this.formVisible.set(true);
    this.passwordFormVisible.set(false);
  }

  cancelForm(): void {
    this.formVisible.set(false);
    this.editingUserId.set(null);
    this.operationError.set(null);
  }

  onRoleChange(): void {
    if (this.form.role === 'platform_admin') {
      this.form.organizationId = null;
      this.form.tenantId = null;
      this.form.environmentId = null;
      return;
    }

    this.form.organizationId =
      this.form.organizationId
      ?? this.defaultOrganizationId
      ?? this.organizations[0]?.id
      ?? null;

    if (this.form.role === 'organization_admin') {
      this.form.tenantId = null;
      this.form.environmentId = null;
      return;
    }

    this.form.tenantId =
      this.form.tenantId
      ?? this.defaultTenantId
      ?? this.formTenants[0]?.id
      ?? null;

    if (this.form.role === 'tenant_admin') {
      this.form.environmentId = null;
      return;
    }

    this.form.environmentId =
      this.form.environmentId
      ?? this.defaultEnvironmentId
      ?? this.formEnvironments[0]?.id
      ?? null;
  }

  onOrganizationChange(): void {
    if (
      this.form.tenantId
      && !this.formTenants.some(
        tenant => tenant.id === this.form.tenantId,
      )
    ) {
      this.form.tenantId = null;
    }

    this.form.environmentId = null;
    this.onRoleChange();
  }

  onTenantChange(): void {
    if (
      this.form.environmentId
      && !this.formEnvironments.some(
        environment =>
          environment.id === this.form.environmentId,
      )
    ) {
      this.form.environmentId = null;
    }

    if (
      this.form.role !== 'tenant_admin'
      && this.form.role !== 'organization_admin'
      && this.form.role !== 'platform_admin'
    ) {
      this.form.environmentId =
        this.form.environmentId
        ?? this.defaultEnvironmentId
        ?? this.formEnvironments[0]?.id
        ?? null;
    }
  }

  async save(): Promise<void> {
    if (this.saving()) {
      return;
    }

    const editingUserId = this.editingUserId();

    if (
      !editingUserId
      && !this.passwordIsValid()
    ) {
      return;
    }

    this.saving.set(true);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      if (editingUserId) {
        await this.service.update(
          editingUserId,
          this.form,
        );

        this.operationMessage.set(
          'Usuário atualizado com sucesso.',
        );
      } else {
        const createdUser = await this.service.create(
          this.form,
        );

        try {
          await this.service.setPassword(
            createdUser.id,
            this.password,
          );
        } catch {
          this.formVisible.set(false);
          this.operationError.set(
            'Usuário cadastrado, mas a senha não foi definida. Use a ação Redefinir senha.',
          );

          await this.refresh();
          return;
        }

        this.operationMessage.set(
          'Usuário cadastrado com sucesso.',
        );
      }

      this.formVisible.set(false);
      this.editingUserId.set(null);

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.saving.set(false);
    }
  }

  openPassword(
    user: User,
  ): void {
    this.passwordUser.set(user);
    this.password = '';
    this.passwordConfirmation = '';
    this.operationError.set(null);
    this.operationMessage.set(null);
    this.formVisible.set(false);
    this.passwordFormVisible.set(true);
  }

  cancelPassword(): void {
    this.passwordFormVisible.set(false);
    this.passwordUser.set(null);
    this.operationError.set(null);
  }

  async savePassword(): Promise<void> {
    const user = this.passwordUser();

    if (
      !user
      || this.savingPassword()
      || !this.passwordIsValid()
    ) {
      return;
    }

    this.savingPassword.set(true);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      await this.service.setPassword(
        user.id,
        this.password,
      );

      this.passwordFormVisible.set(false);
      this.passwordUser.set(null);
      this.operationMessage.set(
        'Senha redefinida com sucesso.',
      );
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.savingPassword.set(false);
    }
  }

  organizationName(
    organizationId: string | null,
  ): string {
    if (!organizationId) {
      return 'Plataforma';
    }

    return this.organizations.find(
      organization =>
        organization.id === organizationId,
    )?.name ?? organizationId;
  }

  tenantName(
    tenantId: string | null,
  ): string {
    if (!tenantId) {
      return 'Todos';
    }

    return this.tenants.find(
      tenant => tenant.id === tenantId,
    )?.name ?? tenantId;
  }

  environmentName(
    environmentId: string | null,
  ): string {
    if (!environmentId) {
      return 'Todos';
    }

    return this.environments.find(
      environment => environment.id === environmentId,
    )?.name ?? environmentId;
  }

  roleLabel(
    role: UserRole,
  ): string {
    return this.allRoleOptions.find(
      option => option.value === role,
    )?.label ?? role;
  }

  private createEmptyInput(): UserInput {
    const role: UserRole = 'viewer';

    const input: UserInput = {
      organizationId:
        this.defaultOrganizationId
        ?? this.organizations[0]?.id
        ?? null,
      tenantId:
        this.defaultTenantId
        ?? null,
      environmentId:
        this.defaultEnvironmentId
        ?? null,
      name: '',
      email: '',
      role,
      status: 'active',
    };

    this.form = input;
    this.onRoleChange();

    return {
      ...this.form,
    };
  }

  private passwordIsValid(): boolean {
    if (
      this.password.length < 8
      || this.password.length > 128
    ) {
      this.operationError.set(
        'A senha deve possuir entre 8 e 128 caracteres.',
      );
      return false;
    }

    if (this.password !== this.passwordConfirmation) {
      this.operationError.set(
        'A confirmação da senha não corresponde.',
      );
      return false;
    }

    return true;
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return error instanceof Error
        ? error.message
        : 'Não foi possível concluir a operação.';
    }

    if (error.status === 400) {
      return 'Revise o papel e o escopo institucional informados.';
    }

    if (error.status === 403) {
      return 'Seu usuário não possui permissão para esta operação.';
    }

    if (error.status === 404) {
      return 'O usuário ou recurso de escopo não foi encontrado.';
    }

    if (error.status === 409) {
      return 'Já existe um usuário com este e-mail na organização.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados no formulário.';
    }

    return 'Não foi possível concluir a operação.';
  }

}