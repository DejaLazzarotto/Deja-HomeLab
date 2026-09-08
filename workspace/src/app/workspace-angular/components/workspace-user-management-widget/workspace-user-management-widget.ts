import {
  HttpClient,
} from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  Input,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import {
  firstValueFrom,
} from 'rxjs';

import {
  Client,
  ClientsComposition,
} from '../../../deja-chamados/clients';

import {
  ClientUsersComposition,
} from '../../../deja-chamados/client-users';

import {
  AuthenticationService,
} from '../../../platform/authentication/application/authentication.service';

import {
  UserClientOption,
  UserEnvironmentOption,
  UserListComponent,
  UserOrganizationOption,
  UsersComposition,
  UserTenantOption,
} from '../../../platform/users';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetContext,
} from '../../../core/workspace-sdk/runtime/workspace-widget-context';

interface OrganizationResponse {
  readonly id: string;
  readonly name: string;
}

interface TenantResponse {
  readonly id: string;
  readonly organization_id: string;
  readonly name: string;
}

interface EnvironmentResponse {
  readonly id: string;
  readonly tenant_id: string;
  readonly name: string;
}

@Component({
  selector: 'deja-workspace-user-management-widget',
  standalone: true,
  imports: [
    UserListComponent,
  ],
  template: `
    @if (loadingScope()) {
      <div class="scope-state">
        Carregando organizações, tenants, ambientes e clientes...
      </div>
    } @else if (scopeError()) {
      <div class="scope-state scope-state--error">
        <p>{{ scopeError() }}</p>

        <button
          type="button"
          (click)="loadScope()"
        >
          Tentar novamente
        </button>
      </div>
    } @else if (currentUser) {
      <deja-user-list
        [service]="composition.service"
        [clientUserLinkService]="clientUsersComposition.service"
        [currentUserRole]="currentUser.role"
        [organizations]="organizations()"
        [tenants]="tenants()"
        [environments]="environments()"
        [clients]="clients()"
        [defaultOrganizationId]="currentUser.organizationId"
        [defaultTenantId]="currentUser.tenantId"
        [defaultEnvironmentId]="currentUser.environmentId"
      />
    }
  `,
  styles: `
    :host {
      display: block;
      min-width: 0;
    }

    .scope-state {
      padding: var(--workspace-spacing-lg);
      color: var(--workspace-color-text-secondary);
      font-size: 0.85rem;
      text-align: center;
      background: var(--workspace-color-surface);
      border: 1px solid var(--workspace-color-border);
      border-radius: var(--workspace-radius-lg);
    }

    .scope-state--error {
      color: var(--workspace-color-danger);
    }

    .scope-state p {
      margin: 0 0 var(--workspace-spacing-md);
    }

    .scope-state button {
      min-height: 2.5rem;
      padding: 0.65rem 1rem;
      color: #fff;
      font: inherit;
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      background: var(--workspace-color-primary);
      border: 0;
      border-radius: var(--workspace-radius-md);
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceUserManagementWidgetComponent
implements OnInit {

  private readonly http = inject(HttpClient);

  private readonly authentication =
    inject(AuthenticationService);

  protected readonly currentUser =
    this.authentication.user();

  protected readonly composition =
    new UsersComposition(
      this.http,
    );

  protected readonly clientsComposition =
    new ClientsComposition(
      this.http,
    );

  protected readonly clientUsersComposition =
    new ClientUsersComposition(
      this.http,
    );

  protected readonly organizations =
    signal<readonly UserOrganizationOption[]>([]);

  protected readonly tenants =
    signal<readonly UserTenantOption[]>([]);

  protected readonly environments =
    signal<readonly UserEnvironmentOption[]>([]);

  protected readonly clients =
    signal<readonly UserClientOption[]>([]);

  protected readonly loadingScope =
    signal(false);

  protected readonly scopeError =
    signal<string | null>(null);

  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

  ngOnInit(): void {
    void this.loadScope();
  }

  protected async loadScope(): Promise<void> {
    this.loadingScope.set(true);
    this.scopeError.set(null);

    try {
      const currentUser = this.currentUser;

      const [
        organizations,
        tenants,
        environments,
        clients,
      ] = await Promise.all([
        firstValueFrom(
          this.http.get<readonly OrganizationResponse[]>(
            '/api/v1/organizations',
          ),
        ),
        firstValueFrom(
          this.http.get<readonly TenantResponse[]>(
            '/api/v1/tenants',
          ),
        ),
        firstValueFrom(
          this.http.get<readonly EnvironmentResponse[]>(
            '/api/v1/environments',
          ),
        ),
        this.clientsComposition.service.list({
          organizationId:
            currentUser?.organizationId
            ?? undefined,
          tenantId:
            currentUser?.tenantId
            ?? undefined,
          environmentId:
            currentUser?.environmentId
            ?? undefined,
          active: true,
        }),
      ]);

      this.organizations.set(
        organizations.map(organization => ({
          id: organization.id,
          name: organization.name,
        })),
      );

      this.tenants.set(
        tenants.map(tenant => ({
          id: tenant.id,
          organizationId: tenant.organization_id,
          name: tenant.name,
        })),
      );

      this.environments.set(
        environments.map(environment => ({
          id: environment.id,
          tenantId: environment.tenant_id,
          name: environment.name,
        })),
      );

      this.clients.set(
        clients.map(
          (client: Client): UserClientOption => ({
            id: client.id,
            organizationId: client.organizationId,
            tenantId: client.tenantId,
            environmentId: client.environmentId,
            name:
              client.fantasyName
              || client.companyName,
            active: client.active,
          }),
        ),
      );
    } catch {
      this.scopeError.set(
        'Não foi possível carregar os dados de organização, tenant, ambiente e clientes.',
      );
    } finally {
      this.loadingScope.set(false);
    }
  }

}