/*
 * Deja Indicadores
 *
 * Indicators Presentation
 *
 * Componente operacional de gerenciamento de indicadores.
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
  Indicator,
  IndicatorInput,
  IndicatorService,
} from '../../index';

export interface IndicatorCompanyOption {
  readonly id: string;
  readonly name: string;
}

@Component({
  selector: 'deja-indicator-list',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './indicator-list.html',
  styleUrl: './indicator-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IndicatorListComponent implements OnInit {

  @Input({
    required: true,
  })
  service!: IndicatorService;

  @Input()
  companies: readonly IndicatorCompanyOption[] = [];

  @Input()
  canEdit = false;

  @Input()
  canDelete = false;

  readonly indicators =
    signal<readonly Indicator[]>([]);

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly deletingIndicatorId =
    signal<string | null>(null);

  readonly formVisible = signal(false);

  readonly editingIndicatorId =
    signal<string | null>(null);

  readonly errorMessage =
    signal<string | null>(null);

  readonly operationMessage =
    signal<string | null>(null);

  readonly operationError =
    signal<string | null>(null);

  form: IndicatorInput =
    this.createEmptyInput();

  ngOnInit(): void {
    void this.refresh();
  }

  async refresh(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      this.indicators.set(
        await this.service.list(),
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar os indicadores.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openCreate(): void {
    if (!this.canEdit || this.companies.length === 0) {
      return;
    }

    this.editingIndicatorId.set(null);
    this.operationError.set(null);
    this.operationMessage.set(null);

    this.form = this.createEmptyInput(
      this.companies[0].id,
    );

    this.formVisible.set(true);
  }

  openEdit(
    indicator: Indicator,
  ): void {
    if (!this.canEdit) {
      return;
    }

    this.editingIndicatorId.set(indicator.id);
    this.operationError.set(null);
    this.operationMessage.set(null);

    this.form = {
      companyId: indicator.companyId,
      name: indicator.name,
      description: indicator.description,
      unit: indicator.unit,
      direction: indicator.direction,
      targetValue: indicator.targetValue,
      status: indicator.status,
    };

    this.formVisible.set(true);
  }

  cancelForm(): void {
    this.formVisible.set(false);
    this.editingIndicatorId.set(null);
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
      const indicatorId =
        this.editingIndicatorId();

      if (indicatorId) {
        await this.service.update(
          indicatorId,
          this.form,
        );

        this.operationMessage.set(
          'Indicador atualizado com sucesso.',
        );
      } else {
        await this.service.create(this.form);

        this.operationMessage.set(
          'Indicador cadastrado com sucesso.',
        );
      }

      this.formVisible.set(false);
      this.editingIndicatorId.set(null);

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.saving.set(false);
    }
  }

  async deleteIndicator(
    indicator: Indicator,
  ): Promise<void> {
    if (
      !this.canDelete
      || this.deletingIndicatorId()
      || !window.confirm(
        `Excluir o indicador "${indicator.name}"?`,
      )
    ) {
      return;
    }

    this.deletingIndicatorId.set(indicator.id);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      await this.service.delete(indicator.id);

      this.operationMessage.set(
        'Indicador excluído com sucesso.',
      );

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.deletingIndicatorId.set(null);
    }
  }

  companyName(
    companyId: string,
  ): string {
    return this.companies.find(
      company => company.id === companyId,
    )?.name ?? companyId;
  }

  directionLabel(
    indicator: Indicator,
  ): string {
    return indicator.direction === 'higher_is_better'
      ? 'Maior é melhor'
      : 'Menor é melhor';
  }

  formatTarget(
    targetValue: number,
  ): string {
    return new Intl.NumberFormat(
      'pt-BR',
      {
        maximumFractionDigits: 4,
      },
    ).format(targetValue);
  }

  private createEmptyInput(
    companyId = '',
  ): IndicatorInput {
    return {
      companyId,
      name: '',
      description: '',
      unit: '',
      direction: 'higher_is_better',
      targetValue: 0,
      status: 'active',
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
      return 'O indicador ou a empresa não foi encontrado.';
    }

    if (error.status === 409) {
      return 'Já existe um indicador com este nome na empresa ou há dados vinculados.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados no formulário.';
    }

    return 'Não foi possível concluir a operação.';
  }

}