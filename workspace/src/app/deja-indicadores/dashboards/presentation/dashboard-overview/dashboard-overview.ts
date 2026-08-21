/*
 * Deja Indicadores
 *
 * Dashboards Presentation
 *
 * Visão gerencial dos indicadores operacionais.
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
  Dashboard,
  DashboardIndicator,
  DashboardService,
  DashboardStatusCount,
} from '../../index';

export interface DashboardCompanyOption {
  readonly id: string;
  readonly name: string;
}

export interface DashboardIndicatorOption {
  readonly id: string;
  readonly companyId: string;
  readonly name: string;
}

export interface DashboardOrganizationOption {
  readonly id: string;
  readonly name: string;
}

export interface DashboardTenantOption {
  readonly id: string;
  readonly organizationId: string;
  readonly name: string;
}

export interface DashboardEnvironmentOption {
  readonly id: string;
  readonly tenantId: string;
  readonly name: string;
}

@Component({
  selector: 'deja-dashboard-overview',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './dashboard-overview.html',
  styleUrl: './dashboard-overview.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardOverviewComponent
implements OnInit {

  @Input({
    required: true,
  })
  service!: DashboardService;

  @Input()
  companies: readonly DashboardCompanyOption[] = [];

  @Input()
  indicators: readonly DashboardIndicatorOption[] = [];

  @Input()
  organizations:
    readonly DashboardOrganizationOption[] = [];

  @Input()
  tenants: readonly DashboardTenantOption[] = [];

  @Input()
  environments:
    readonly DashboardEnvironmentOption[] = [];

  @Input()
  defaultOrganizationId: string | null = null;

  @Input()
  defaultTenantId: string | null = null;

  @Input()
  defaultEnvironmentId: string | null = null;

  readonly dashboard = signal<Dashboard | null>(null);

  readonly loading = signal(false);

  readonly errorMessage = signal<string | null>(null);

  filterCompanyId = '';
  filterIndicatorId = '';
  filterOrganizationId = '';
  filterTenantId = '';
  filterEnvironmentId = '';
  filterStartDate = '';
  filterEndDate = '';

  ngOnInit(): void {
    this.filterOrganizationId =
      this.defaultOrganizationId ?? '';

    this.filterTenantId =
      this.defaultTenantId ?? '';

    this.filterEnvironmentId =
      this.defaultEnvironmentId ?? '';

    void this.refresh();
  }

  async refresh(): Promise<void> {
    if (
      this.filterStartDate
      && this.filterEndDate
      && this.filterStartDate > this.filterEndDate
    ) {
      this.errorMessage.set(
        'A data inicial não pode ser posterior à data final.',
      );

      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      this.dashboard.set(
        await this.service.getOverview({
          companyId:
            this.filterCompanyId || undefined,
          indicatorId:
            this.filterIndicatorId || undefined,
          organizationId:
            this.filterOrganizationId || undefined,
          tenantId:
            this.filterTenantId || undefined,
          environmentId:
            this.filterEnvironmentId || undefined,
          startDate:
            this.filterStartDate || undefined,
          endDate:
            this.filterEndDate || undefined,
        }),
      );
    } catch (error: unknown) {
      this.errorMessage.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.loading.set(false);
    }
  }

  applyFilters(): void {
    void this.refresh();
  }

  clearFilters(): void {
    this.filterCompanyId = '';
    this.filterIndicatorId = '';
    this.filterOrganizationId =
      this.defaultOrganizationId ?? '';
    this.filterTenantId =
      this.defaultTenantId ?? '';
    this.filterEnvironmentId =
      this.defaultEnvironmentId ?? '';
    this.filterStartDate = '';
    this.filterEndDate = '';

    void this.refresh();
  }

  companyChanged(): void {
    if (
      this.filterIndicatorId
      && !this.indicators.some(
        indicator =>
          indicator.id === this.filterIndicatorId
          && indicator.companyId === this.filterCompanyId,
      )
    ) {
      this.filterIndicatorId = '';
    }
  }

  organizationChanged(): void {
    if (
      this.filterTenantId
      && !this.tenants.some(
        tenant =>
          tenant.id === this.filterTenantId
          && tenant.organizationId
            === this.filterOrganizationId,
      )
    ) {
      this.filterTenantId = '';
      this.filterEnvironmentId = '';
    }
  }

  tenantChanged(): void {
    if (
      this.filterEnvironmentId
      && !this.environments.some(
        environment =>
          environment.id
            === this.filterEnvironmentId
          && environment.tenantId
            === this.filterTenantId,
      )
    ) {
      this.filterEnvironmentId = '';
    }
  }

  filteredIndicators():
  readonly DashboardIndicatorOption[] {
    if (!this.filterCompanyId) {
      return this.indicators;
    }

    return this.indicators.filter(
      indicator =>
        indicator.companyId
          === this.filterCompanyId,
    );
  }

  filteredTenants():
  readonly DashboardTenantOption[] {
    if (!this.filterOrganizationId) {
      return this.tenants;
    }

    return this.tenants.filter(
      tenant =>
        tenant.organizationId
          === this.filterOrganizationId,
    );
  }

  filteredEnvironments():
  readonly DashboardEnvironmentOption[] {
    if (!this.filterTenantId) {
      return this.environments;
    }

    return this.environments.filter(
      environment =>
        environment.tenantId
          === this.filterTenantId,
    );
  }

  statusCount(
    counts: readonly DashboardStatusCount[],
    status: string,
  ): number {
    return counts.find(
      item => item.status === status,
    )?.count ?? 0;
  }

  situationLabel(
    indicator: DashboardIndicator,
  ): string {
    switch (indicator.situation) {
      case 'on_target':
        return 'Meta atendida';
      case 'below_target':
        return 'Abaixo da meta';
      case 'above_target':
        return 'Acima da meta';
      default:
        return 'Sem medição';
    }
  }

  situationClass(
    indicator: DashboardIndicator,
  ): string {
    return `indicator-card--${indicator.situation}`;
  }

  directionLabel(
    indicator: DashboardIndicator,
  ): string {
    return indicator.direction
      === 'higher_is_better'
      ? 'Maior é melhor'
      : 'Menor é melhor';
  }

  formatValue(
    value: number,
    unit: string,
  ): string {
    const formatted = new Intl.NumberFormat(
      'pt-BR',
      {
        maximumFractionDigits: 4,
      },
    ).format(value);

    return unit
      ? `${formatted} ${unit}`
      : formatted;
  }

  formatPercentage(
    value: number | null,
  ): string {
    if (value === null) {
      return '—';
    }

    return `${new Intl.NumberFormat(
      'pt-BR',
      {
        maximumFractionDigits: 1,
      },
    ).format(value)}%`;
  }

  formatDate(
    value: string,
  ): string {
    return new Intl.DateTimeFormat(
      'pt-BR',
    ).format(
      new Date(`${value}T00:00:00`),
    );
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return 'Não foi possível carregar o dashboard.';
    }

    if (error.status === 403) {
      return 'Seu usuário não possui acesso a este escopo.';
    }

    if (error.status === 404) {
      return 'Um dos filtros informados não foi encontrado.';
    }

    if (error.status === 422) {
      return 'Revise o período e os filtros informados.';
    }

    return 'Não foi possível carregar o dashboard.';
  }

}