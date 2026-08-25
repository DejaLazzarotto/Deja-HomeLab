/*
 * Deja Workspace Angular Integration
 *
 * Management Report Widget
 *
 * Integra o relatório gerencial à FastAPI.
 */

import { HttpClient } from '@angular/common/http';

import { ChangeDetectionStrategy, Component, Input, OnInit, inject, signal } from '@angular/core';

import { firstValueFrom } from 'rxjs';

import { AuthenticationService } from '../../../platform/authentication/application/authentication.service';

import {
  DashboardCompanyOption,
  DashboardEnvironmentOption,
  DashboardIndicatorOption,
  DashboardOrganizationOption,
  DashboardTenantOption,
} from '../../../deja-indicadores/dashboards';

import { ManagementReportComponent, ReportsComposition } from '../../../deja-indicadores/reports';

import { WorkspaceWidgetInstance } from '../../../core/workspace-sdk/runtime/workspace-widget';

import { WorkspaceWidgetContext } from '../../../core/workspace-sdk/runtime/workspace-widget-context';

interface CompanyResponse {
  readonly id: string;
  readonly trade_name: string;
  readonly legal_name: string;
}

interface IndicatorResponse {
  readonly id: string;
  readonly company_id: string;
  readonly name: string;
}

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
  selector: 'deja-workspace-management-report-widget',
  standalone: true,
  imports: [ManagementReportComponent],
  template: `
    @if (loadingOptions()) {
      <div class="widget-state">Carregando filtros do relatório...</div>
    } @else if (optionsError()) {
      <div class="widget-state widget-state--error">
        <p>{{ optionsError() }}</p>

        <button type="button" (click)="loadOptions()">Tentar novamente</button>
      </div>
    } @else if (currentUser) {
      <deja-management-report
        [service]="composition.service"
        [companies]="companies()"
        [indicators]="indicators()"
        [organizations]="organizations()"
        [tenants]="tenants()"
        [environments]="environments()"
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

    .widget-state {
      padding: var(--workspace-spacing-lg);
      color: var(--workspace-color-text-secondary);
      font-size: 0.85rem;
      text-align: center;
      background: var(--workspace-color-surface);
      border: 1px solid var(--workspace-color-border);
      border-radius: var(--workspace-radius-lg);
    }

    .widget-state--error {
      color: var(--workspace-color-danger);
    }

    .widget-state p {
      margin: 0 0 var(--workspace-spacing-md);
    }

    .widget-state button {
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
export class WorkspaceManagementReportWidgetComponent implements OnInit {
  private readonly http = inject(HttpClient);

  private readonly authentication = inject(AuthenticationService);

  protected readonly currentUser = this.authentication.user();

  private readonly canLoadScopeOptions = [
    'platform_admin',
    'organization_admin',
    'tenant_admin',
  ].includes(this.currentUser?.role ?? '');

  protected readonly composition = new ReportsComposition(this.http);

  protected readonly companies = signal<readonly DashboardCompanyOption[]>([]);

  protected readonly indicators = signal<readonly DashboardIndicatorOption[]>([]);

  protected readonly organizations = signal<readonly DashboardOrganizationOption[]>([]);

  protected readonly tenants = signal<readonly DashboardTenantOption[]>([]);

  protected readonly environments = signal<readonly DashboardEnvironmentOption[]>([]);

  protected readonly loadingOptions = signal(false);

  protected readonly optionsError = signal<string | null>(null);

  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

  ngOnInit(): void {
    void this.loadOptions();
  }

  protected async loadOptions(): Promise<void> {
    this.loadingOptions.set(true);
    this.optionsError.set(null);

    try {
      const [
        companies,
        indicators,
      ] = await Promise.all([
        firstValueFrom(
          this.http.get<readonly CompanyResponse[]>(
            '/api/companies',
          ),
        ),
        firstValueFrom(
          this.http.get<readonly IndicatorResponse[]>(
            '/api/indicators',
          ),
        ),
      ]);

      this.companies.set(
        companies.map(company => ({
          id: company.id,
          name:
            company.trade_name
            || company.legal_name,
        })),
      );

      this.indicators.set(
        indicators.map(indicator => ({
          id: indicator.id,
          companyId: indicator.company_id,
          name: indicator.name,
        })),
      );

      if (this.canLoadScopeOptions) {
        const [
          organizations,
          tenants,
          environments,
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
            organizationId:
              tenant.organization_id,
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
      } else {
        const organizationId =
          this.currentUser?.organizationId;

        const tenantId =
          this.currentUser?.tenantId;

        const environmentId =
          this.currentUser?.environmentId;

        this.organizations.set(
          organizationId
            ? [{
                id: organizationId,
                name: 'Organização atual',
              }]
            : [],
        );

        this.tenants.set(
          tenantId
            ? [{
                id: tenantId,
                organizationId:
                  organizationId ?? '',
                name: 'Tenant atual',
              }]
            : [],
        );

        this.environments.set(
          environmentId
            ? [{
                id: environmentId,
                tenantId: tenantId ?? '',
                name: 'Ambiente atual',
              }]
            : [],
        );
      }
    } catch {
      this.optionsError.set(
        'Não foi possível carregar os filtros do relatório.',
      );
    } finally {
      this.loadingOptions.set(false);
    }
  }
}
