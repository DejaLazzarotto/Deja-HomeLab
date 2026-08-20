/*
 * Deja Indicadores
 *
 * Measurements Presentation
 *
 * Componente operacional da Coleta Manual.
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
  Measurement,
  MeasurementInput,
  MeasurementService,
} from '../../index';

export interface MeasurementCompanyOption {
  readonly id: string;
  readonly name: string;
}

export interface MeasurementIndicatorOption {
  readonly id: string;
  readonly companyId: string;
  readonly name: string;
  readonly unit: string;
  readonly status: 'active' | 'inactive';
}

@Component({
  selector: 'deja-measurement-list',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './measurement-list.html',
  styleUrl: './measurement-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MeasurementListComponent implements OnInit {

  @Input({
    required: true,
  })
  service!: MeasurementService;

  @Input()
  companies: readonly MeasurementCompanyOption[] = [];

  @Input()
  indicators: readonly MeasurementIndicatorOption[] = [];

  @Input()
  canEdit = false;

  @Input()
  canDelete = false;

  readonly measurements =
    signal<readonly Measurement[]>([]);

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly deletingMeasurementId =
    signal<string | null>(null);

  readonly formVisible = signal(false);

  readonly editingMeasurementId =
    signal<string | null>(null);

  readonly errorMessage =
    signal<string | null>(null);

  readonly operationMessage =
    signal<string | null>(null);

  readonly operationError =
    signal<string | null>(null);

  filterCompanyId = '';
  filterIndicatorId = '';
  filterStartDate = '';
  filterEndDate = '';

  formCompanyId = '';

  form: MeasurementInput =
    this.createEmptyInput();

  ngOnInit(): void {
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
      this.measurements.set(
        await this.service.list({
          companyId:
            this.filterCompanyId || undefined,
          indicatorId:
            this.filterIndicatorId || undefined,
          startDate:
            this.filterStartDate || undefined,
          endDate:
            this.filterEndDate || undefined,
        }),
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar as medições.',
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
    this.filterStartDate = '';
    this.filterEndDate = '';

    void this.refresh();
  }

  filterCompanyChanged(): void {
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

  openCreate(): void {
    if (!this.canEdit) {
      return;
    }

    const indicator =
      this.indicators.find(
        item => item.status === 'active',
      );

    if (!indicator) {
      return;
    }

    this.editingMeasurementId.set(null);
    this.operationError.set(null);
    this.operationMessage.set(null);

    this.formCompanyId = indicator.companyId;
    this.form = this.createEmptyInput(indicator.id);
    this.formVisible.set(true);
  }

  openEdit(
    measurement: Measurement,
  ): void {
    if (!this.canEdit) {
      return;
    }

    const indicator = this.indicator(
      measurement.indicatorId,
    );

    this.editingMeasurementId.set(measurement.id);
    this.operationError.set(null);
    this.operationMessage.set(null);

    this.formCompanyId =
      indicator?.companyId ?? '';

    this.form = {
      indicatorId: measurement.indicatorId,
      referenceDate: measurement.referenceDate,
      actualValue: measurement.actualValue,
      observation: measurement.observation,
    };

    this.formVisible.set(true);
  }

  formCompanyChanged(): void {
    const indicator =
      this.formIndicators().find(
        item => item.status === 'active',
      );

    this.form = {
      ...this.form,
      indicatorId: indicator?.id ?? '',
    };
  }

  cancelForm(): void {
    this.formVisible.set(false);
    this.editingMeasurementId.set(null);
    this.operationError.set(null);
  }

  async save(): Promise<void> {
    if (!this.canEdit || this.saving()) {
      return;
    }

    this.saving.set(true);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      const measurementId =
        this.editingMeasurementId();

      if (measurementId) {
        await this.service.update(
          measurementId,
          this.form,
        );

        this.operationMessage.set(
          'Medição atualizada com sucesso.',
        );
      } else {
        await this.service.create(this.form);

        this.operationMessage.set(
          'Medição lançada com sucesso.',
        );
      }

      this.formVisible.set(false);
      this.editingMeasurementId.set(null);

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.saving.set(false);
    }
  }

  async deleteMeasurement(
    measurement: Measurement,
  ): Promise<void> {
    if (
      !this.canDelete
      || this.deletingMeasurementId()
      || !window.confirm(
        'Excluir esta medição manual?',
      )
    ) {
      return;
    }

    this.deletingMeasurementId.set(
      measurement.id,
    );

    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      await this.service.delete(measurement.id);

      this.operationMessage.set(
        'Medição excluída com sucesso.',
      );

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.deletingMeasurementId.set(null);
    }
  }

  filteredIndicators():
  readonly MeasurementIndicatorOption[] {
    if (!this.filterCompanyId) {
      return this.indicators;
    }

    return this.indicators.filter(
      indicator =>
        indicator.companyId === this.filterCompanyId,
    );
  }

  formIndicators():
  readonly MeasurementIndicatorOption[] {
    return this.indicators.filter(
      indicator =>
        indicator.companyId === this.formCompanyId
        && (
          indicator.status === 'active'
          || indicator.id === this.form.indicatorId
        ),
    );
  }

  hasActiveIndicators(): boolean {
    return this.indicators.some(
      indicator => indicator.status === 'active',
    );
  }

  companyName(
    measurement: Measurement,
  ): string {
    const companyId =
      this.indicator(
        measurement.indicatorId,
      )?.companyId;

    if (!companyId) {
      return 'Empresa não identificada';
    }

    return this.companies.find(
      company => company.id === companyId,
    )?.name ?? companyId;
  }

  indicatorName(
    indicatorId: string,
  ): string {
    return this.indicator(indicatorId)?.name
      ?? indicatorId;
  }

  formatActualValue(
    measurement: Measurement,
  ): string {
    const value = new Intl.NumberFormat(
      'pt-BR',
      {
        maximumFractionDigits: 4,
      },
    ).format(measurement.actualValue);

    const unit =
      this.indicator(
        measurement.indicatorId,
      )?.unit;

    return unit
      ? `${value} ${unit}`
      : value;
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

  private indicator(
    indicatorId: string,
  ): MeasurementIndicatorOption | undefined {
    return this.indicators.find(
      indicator => indicator.id === indicatorId,
    );
  }

  private createEmptyInput(
    indicatorId = '',
  ): MeasurementInput {
    return {
      indicatorId,
      referenceDate:
        new Date().toISOString().slice(0, 10),
      actualValue: 0,
      observation: '',
    };
  }

  private resolveErrorMessage(
    error: unknown,
  ): string {
    if (!(error instanceof HttpErrorResponse)) {
      return error instanceof Error
        ? error.message
        : 'Não foi possível concluir a operação.';
    }

    if (error.status === 403) {
      return 'Seu usuário não possui permissão para esta operação.';
    }

    if (error.status === 404) {
      return 'A medição ou o indicador não foi encontrado.';
    }

    if (error.status === 409) {
      return 'Já existe uma medição para este indicador e esta data.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados no formulário.';
    }

    return 'Não foi possível concluir a operação.';
  }

}