/*
 * Deja Indicadores
 *
 * Reports Presentation
 *
 * Relatório gerencial dos indicadores operacionais.
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
  DashboardCompanyOption,
  DashboardEnvironmentOption,
  DashboardIndicator,
  DashboardIndicatorOption,
  DashboardOrganizationOption,
  DashboardTenantOption,
} from '../../../dashboards';

import {
  ManagementReport,
  ReportService,
} from '../../index';

@Component({
  selector: 'deja-management-report',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './management-report.html',
  styleUrl: './management-report.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ManagementReportComponent
implements OnInit {

  @Input({
    required: true,
  })
  service!: ReportService;

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

  readonly report =
    signal<ManagementReport | null>(null);

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

    void this.generate();
  }

  async generate(): Promise<void> {
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
      this.report.set(
        await this.service.getManagementReport({
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

    void this.generate();
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
          environment.id === this.filterEnvironmentId
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
        indicator.companyId === this.filterCompanyId,
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

  print(): void {
    window.print();
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
    return `situation situation--${indicator.situation}`;
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

  formatReferenceDate(
    value: string,
  ): string {
    return new Intl.DateTimeFormat(
      'pt-BR',
    ).format(
      new Date(`${value}T00:00:00`),
    );
  }

  formatGeneratedAt(
    value: string,
  ): string {
    return new Intl.DateTimeFormat(
      'pt-BR',
      {
        dateStyle: 'short',
        timeStyle: 'short',
      },
    ).format(new Date(value));
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return 'Não foi possível gerar o relatório.';
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

    return 'Não foi possível gerar o relatório.';
  }

}