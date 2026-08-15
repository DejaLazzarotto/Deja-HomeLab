/*
 * Deja Indicadores
 *
 * Companies Presentation
 *
 * Componente responsável pela apresentação e gerenciamento
 * da listagem de empresas.
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
  Company,
  CompanyInput,
  CompanyService,
} from '../../index';

export interface CompanyEnvironmentOption {
  readonly id: string;
  readonly name: string;
}

@Component({
  selector: 'deja-company-list',
  standalone: true,
  imports: [
    FormsModule,
  ],
  templateUrl: './company-list.html',
  styleUrl: './company-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CompanyListComponent implements OnInit {

  @Input({
    required: true,
  })
  service!: CompanyService;

  @Input()
  environments: readonly CompanyEnvironmentOption[] = [];

  @Input()
  defaultEnvironmentId: string | null = null;

  @Input()
  canManage = false;

  readonly companies = signal<readonly Company[]>([]);

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly deletingCompanyId = signal<string | null>(null);

  readonly formVisible = signal(false);

  readonly editingCompanyId = signal<string | null>(null);

  readonly errorMessage = signal<string | null>(null);

  readonly operationMessage = signal<string | null>(null);

  readonly operationError = signal<string | null>(null);

  form: CompanyInput = this.createEmptyInput();

  ngOnInit(): void {
    void this.refresh();
  }

  async refresh(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      this.companies.set(
        await this.service.list(),
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar as empresas.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  openCreate(): void {
    this.editingCompanyId.set(null);
    this.operationError.set(null);
    this.operationMessage.set(null);

    this.form = this.createEmptyInput(
      this.defaultEnvironmentId
      ?? this.environments[0]?.id
      ?? '',
    );

    this.formVisible.set(true);
  }

  openEdit(
    company: Company,
  ): void {
    this.editingCompanyId.set(company.id);
    this.operationError.set(null);
    this.operationMessage.set(null);

    this.form = {
      environmentId: company.environmentId,
      legalName: company.legalName,
      tradeName: company.tradeName,
      document: company.document,
      email: company.email,
      phone: company.phone,
      status: company.status,
    };

    this.formVisible.set(true);
  }

  cancelForm(): void {
    this.formVisible.set(false);
    this.editingCompanyId.set(null);
    this.operationError.set(null);
  }

  async save(): Promise<void> {
    if (!this.canManage || this.saving()) {
      return;
    }

    this.saving.set(true);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      const companyId = this.editingCompanyId();

      if (companyId) {
        await this.service.update(
          companyId,
          this.form,
        );

        this.operationMessage.set(
          'Empresa atualizada com sucesso.',
        );
      } else {
        await this.service.create(
          this.form,
        );

        this.operationMessage.set(
          'Empresa cadastrada com sucesso.',
        );
      }

      this.formVisible.set(false);
      this.editingCompanyId.set(null);

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.saving.set(false);
    }
  }

  async deleteCompany(
    company: Company,
  ): Promise<void> {
    if (
      !this.canManage
      || this.deletingCompanyId()
      || !window.confirm(
        `Excluir a empresa "${company.tradeName}"?`,
      )
    ) {
      return;
    }

    this.deletingCompanyId.set(company.id);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      await this.service.delete(company.id);

      this.operationMessage.set(
        'Empresa excluída com sucesso.',
      );

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(
        this.resolveErrorMessage(error),
      );
    } finally {
      this.deletingCompanyId.set(null);
    }
  }

  environmentName(
    environmentId: string,
  ): string {
    return this.environments.find(
      environment => environment.id === environmentId,
    )?.name ?? environmentId;
  }

  private createEmptyInput(
    environmentId = '',
  ): CompanyInput {
    return {
      environmentId,
      legalName: '',
      tradeName: '',
      document: '',
      email: '',
      phone: '',
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
      return 'A empresa não foi encontrada.';
    }

    if (error.status === 409) {
      return 'Já existe uma empresa com este documento.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados no formulário.';
    }

    return 'Não foi possível concluir a operação.';
  }

}