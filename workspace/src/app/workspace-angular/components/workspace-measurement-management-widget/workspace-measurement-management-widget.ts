/*
 * Deja Workspace Angular Integration
 *
 * Measurement Management Widget
 *
 * Integra a Coleta Manual ao Workspace institucional.
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
  MeasurementCompanyOption,
  MeasurementIndicatorOption,
  MeasurementListComponent,
  MeasurementsComposition,
} from '../../../deja-indicadores/measurements';

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

interface IndicatorResponse {
  readonly id: string;
  readonly company_id: string;
  readonly name: string;
  readonly unit: string;
  readonly status: 'active' | 'inactive';
}

@Component({
  selector: 'deja-workspace-measurement-management-widget',
  standalone: true,
  imports: [
    MeasurementListComponent,
  ],
  template: `
    <deja-measurement-list
      [service]="composition.service"
      [companies]="companies()"
      [indicators]="indicators()"
      [canEdit]="canEdit"
      [canDelete]="canDelete"
    />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceMeasurementManagementWidgetComponent
implements OnInit {

  private readonly http = inject(HttpClient);

  private readonly authentication =
    inject(AuthenticationService);

  private readonly currentUser =
    this.authentication.user();

  protected readonly composition =
    new MeasurementsComposition(this.http);

  protected readonly companies =
    signal<readonly MeasurementCompanyOption[]>([]);

  protected readonly indicators =
    signal<readonly MeasurementIndicatorOption[]>([]);

  protected readonly canEdit = [
    'platform_admin',
    'organization_admin',
    'tenant_admin',
    'manager',
    'analyst',
  ].includes(
    this.currentUser?.role ?? '',
  );

  protected readonly canDelete = this.canEdit;

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

  private async loadOptions(): Promise<void> {
    try {
      const [
        companyResponse,
        indicatorResponse,
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
        companyResponse.map(company => ({
          id: company.id,
          name:
            company.trade_name
            || company.legal_name,
        })),
      );

      this.indicators.set(
        indicatorResponse.map(indicator => ({
          id: indicator.id,
          companyId: indicator.company_id,
          name: indicator.name,
          unit: indicator.unit,
          status: indicator.status,
        })),
      );
    } catch {
      this.companies.set([]);
      this.indicators.set([]);
    }
  }

}