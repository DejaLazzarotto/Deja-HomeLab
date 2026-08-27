/*
 * Deja Chamados
 *
 * Clients Presentation
 *
 * Coordena a consulta e o gerenciamento visual dos clientes.
 */

import { HttpErrorResponse } from '@angular/common/http';

import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
  input,
  signal,
} from '@angular/core';

import { FormsModule } from '@angular/forms';

import { ClientService } from '../../application';

import { Client, ClientFilters, ClientInput } from '../../domain';

import { ClientEnvironmentOption } from '../client-environment-option';

import { ClientFormComponent } from '../client-form/client-form';

import { ClientListComponent } from '../client-list/client-list';

type ClientActiveFilter = 'all' | 'active' | 'inactive';

@Component({
  selector: 'deja-client-management',
  standalone: true,
  imports: [
    FormsModule,
    ClientFormComponent,
    ClientListComponent,
  ],
  templateUrl: './client-management.html',
  styleUrl: './client-management.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClientManagementComponent implements OnInit, OnDestroy {
  readonly service = input.required<ClientService>();

  readonly environments = input<readonly ClientEnvironmentOption[]>([]);

  readonly defaultEnvironmentId = input<string | null>(null);

  readonly canManage = input(false);

  readonly clients = signal<readonly Client[]>([]);

  readonly searchTerm = signal('');

  readonly activeFilter = signal<ClientActiveFilter>('all');

  readonly loading = signal(false);

  readonly saving = signal(false);

  readonly deletingClientId = signal<string | null>(null);

  readonly selectedClient = signal<Client | null>(null);

  readonly formVisible = signal(false);

  readonly errorMessage = signal<string | null>(null);

  readonly operationMessage = signal<string | null>(null);

  readonly operationError = signal<string | null>(null);

  private searchTimer: ReturnType<typeof setTimeout> | null = null;

  private requestSequence = 0;

  ngOnInit(): void {
    void this.refresh();
  }

  ngOnDestroy(): void {
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }
  }

  async refresh(): Promise<void> {
    const requestSequence = this.requestSequence + 1;

    this.requestSequence = requestSequence;

    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const clients = await this.service().list(this.createFilters());

      if (requestSequence === this.requestSequence) {
        this.clients.set(clients);
      }
    } catch {
      if (requestSequence === this.requestSequence) {
        this.errorMessage.set('Não foi possível carregar os clientes.');
      }
    } finally {
      if (requestSequence === this.requestSequence) {
        this.loading.set(false);
      }
    }
  }

  onSearchTermChange(value: string): void {
    this.searchTerm.set(value);

    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }

    this.searchTimer = setTimeout(() => {
      this.searchTimer = null;
      void this.refresh();
    }, 300);
  }

  onActiveFilterChange(value: ClientActiveFilter): void {
    this.activeFilter.set(value);

    void this.refresh();
  }

  openCreate(): void {
    if (!this.canManage()) {
      return;
    }

    this.selectedClient.set(null);
    this.operationError.set(null);
    this.operationMessage.set(null);
    this.formVisible.set(true);
    this.scrollToForm();
  }

  openEdit(client: Client): void {
    if (!this.canManage()) {
      return;
    }

    this.selectedClient.set(client);

    this.operationError.set(null);
    this.operationMessage.set(null);
    this.formVisible.set(true);
    this.scrollToForm();
  }

  closeForm(): void {
    if (this.saving()) {
      return;
    }

    this.selectedClient.set(null);
    this.formVisible.set(false);
    this.operationError.set(null);
  }

  async saveClient(input: ClientInput): Promise<void> {
    if (!this.canManage() || this.saving()) {
      return;
    }

    this.saving.set(true);
    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      const selectedClient = this.selectedClient();

      if (selectedClient) {
        await this.service().update(selectedClient.id, input);

        this.operationMessage.set('Cliente atualizado com sucesso.');
      } else {
        await this.service().create(input);

        this.operationMessage.set('Cliente cadastrado com sucesso.');
      }

      this.selectedClient.set(null);
      this.formVisible.set(false);

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(this.resolveErrorMessage(error));
    } finally {
      this.saving.set(false);
    }
  }

  async deleteClient(clientId: string): Promise<void> {
    if (!this.canManage() || this.deletingClientId()) {
      return;
    }

    const client = this.clients().find((item) => item.id === clientId);

    const clientName = client?.fantasyName ?? 'este cliente';

    if (!window.confirm(`Excluir o cliente "${clientName}"?`)) {
      return;
    }

    this.deletingClientId.set(clientId);

    this.operationError.set(null);
    this.operationMessage.set(null);

    try {
      await this.service().delete(clientId);

      if (this.selectedClient()?.id === clientId) {
        this.selectedClient.set(null);
        this.formVisible.set(false);
      }

      this.operationMessage.set('Cliente excluído com sucesso.');

      await this.refresh();
    } catch (error: unknown) {
      this.operationError.set(this.resolveErrorMessage(error));
    } finally {
      this.deletingClientId.set(null);
    }
  }

  private createFilters(): ClientFilters {
    const search = this.searchTerm().trim();

    const activeFilter = this.activeFilter();

    return {
      search: search || undefined,
      active: activeFilter === 'all' ? undefined : activeFilter === 'active',
    };
  }

  private resolveErrorMessage(error: unknown): string {
    if (!(error instanceof HttpErrorResponse)) {
      return error instanceof Error ? error.message : 'Não foi possível concluir a operação.';
    }

    if (error.status === 0) {
      return 'Não foi possível acessar a API.';
    }

    if (error.status === 403) {
      return 'Seu usuário não possui permissão para esta operação.';
    }

    if (error.status === 404) {
      return 'O cliente não foi encontrado.';
    }

    if (error.status === 409) {
      return 'Já existe um cliente com este documento nesta organização.';
    }

    if (error.status === 422) {
      return 'Revise os dados informados no formulário.';
    }

    return 'Não foi possível concluir a operação.';
  }

  private scrollToForm(): void {
    setTimeout(() => {
      document.querySelector('deja-client-form')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    });
  }
}
