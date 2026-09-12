/*
 * Deja Workspace Angular Integration
 *
 * Ticket Management Widget
 *
 * Integra a Gestão de Chamados ao Workspace institucional.
 */

import { HttpClient } from '@angular/common/http';

import { ChangeDetectionStrategy, Component, Input, OnInit, inject, signal } from '@angular/core';

import { Client, ClientsComposition } from '../../../deja-chamados/clients';

import { TicketManagementComponent, TicketsComposition } from '../../../deja-chamados/tickets';

import { AuthenticationService } from '../../../platform/authentication/application/authentication.service';

import { WorkspaceWidgetInstance } from '../../../core/workspace-sdk/runtime/workspace-widget';

import { WorkspaceWidgetContext } from '../../../core/workspace-sdk/runtime/workspace-widget-context';

@Component({
  selector: 'deja-workspace-ticket-management-widget',
  standalone: true,
  imports: [TicketManagementComponent],
  template: `
    @if (loadingClients()) {
      <div class="scope-state">Carregando clientes...</div>
    } @else if (clientError()) {
      <div class="scope-state scope-state--error">
        <p>{{ clientError() }}</p>

        <button type="button" (click)="loadClients()">Tentar novamente</button>
      </div>
    } @else {
      <deja-ticket-management
        [service]="ticketsComposition.service"
        [assigneeService]="ticketsComposition.assigneeService"
        [timelineService]="ticketsComposition.timelineService"
        [commentService]="ticketsComposition.commentService"
        [attachmentService]="ticketsComposition.attachmentService"
        [clients]="clients()"
        [canManage]="canManage"
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
      color: var(--workspace-color-primary-contrast);
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
export class WorkspaceTicketManagementWidgetComponent implements OnInit {
  private readonly http = inject(HttpClient);

  private readonly authentication = inject(AuthenticationService);

  private readonly clientsComposition = new ClientsComposition(this.http);

  protected readonly ticketsComposition = new TicketsComposition(this.http);

  protected readonly clients = signal<readonly Client[]>([]);

  protected readonly loadingClients = signal(false);

  protected readonly clientError = signal<string | null>(null);

  protected readonly currentUser = this.authentication.user();

  protected readonly canManage = [
    'platform_admin',
    'organization_admin',
    'tenant_admin',
    'manager',
    'analyst',
  ].includes(this.currentUser?.role ?? '');

  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

  ngOnInit(): void {
    void this.loadClients();
  }

  protected async loadClients(): Promise<void> {
    this.loadingClients.set(true);
    this.clientError.set(null);

    try {
      this.clients.set(await this.clientsComposition.service.list());
    } catch {
      this.clientError.set('Não foi possível carregar os clientes.');
    } finally {
      this.loadingClients.set(false);
    }
  }
}
