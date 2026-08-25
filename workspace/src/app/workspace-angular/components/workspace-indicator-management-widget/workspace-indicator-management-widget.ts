/*
 * Deja Workspace Angular Integration
 *
 * Indicator Management Widget
 *
 * Integra a Gestão de Indicadores ao Workspace institucional.
 */

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
  AuthenticationService,
} from '../../../platform/authentication/application/authentication.service';

import {
  IndicatorCompanyOption,
  IndicatorListComponent,
  IndicatorsComposition,
} from '../../../deja-indicadores/indicators';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetContext,
} from '../../../core/workspace-sdk/runtime/workspace-widget-context';

interface CompanyResponse {
  readonly id: string;
  readonly trade_name: string;
  readonly legal_name: string;
}

@Component({
  selector: 'deja-workspace-indicator-management-widget',
  standalone: true,
  imports: [
    IndicatorListComponent,
  ],
  template: `
    <deja-indicator-list
      [service]="composition.service"
      [companies]="companies()"
      [canEdit]="canEdit"
      [canDelete]="canDelete"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceIndicatorManagementWidgetComponent
implements OnInit {

  private readonly http = inject(HttpClient);

  private readonly authentication =
    inject(AuthenticationService);

  private readonly currentUser =
    this.authentication.user();

  protected readonly composition =
    new IndicatorsComposition(this.http);

  protected readonly companies =
    signal<readonly IndicatorCompanyOption[]>([]);

  protected readonly canEdit = [
    'platform_admin',
    'organization_admin',
    'tenant_admin',
    'manager',
    'analyst',
  ].includes(
    this.currentUser?.role ?? '',
  );

  protected readonly canDelete = [
    'platform_admin',
    'organization_admin',
    'tenant_admin',
    'manager',
  ].includes(
    this.currentUser?.role ?? '',
  );

  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

  ngOnInit(): void {
    void this.loadCompanies();
  }

  private async loadCompanies(): Promise<void> {
    try {
      const response = await firstValueFrom(
        this.http.get<readonly CompanyResponse[]>(
          '/api/companies',
        ),
      );

      this.companies.set(
        response.map(company => ({
          id: company.id,
          name:
            company.trade_name
            || company.legal_name,
        })),
      );
    } catch {
      this.companies.set([]);
    }
  }

}