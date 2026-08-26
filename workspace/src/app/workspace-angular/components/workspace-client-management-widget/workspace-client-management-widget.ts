/*
 * Deja Workspace Angular Integration
 *
 * Client Management Widget
 *
 * Integra a Gestão de Clientes do Deja Chamados ao Workspace institucional.
 */

import { HttpClient } from '@angular/common/http';

import { ChangeDetectionStrategy, Component, Input, OnInit, inject, signal } from '@angular/core';

import { firstValueFrom } from 'rxjs';

import {
  ClientEnvironmentOption,
  ClientManagementComponent,
  ClientsComposition,
} from '../../../deja-chamados/clients';

import { AuthenticationService } from '../../../platform/authentication/application/authentication.service';

import { WorkspaceWidgetInstance } from '../../../core/workspace-sdk/runtime/workspace-widget';

import { WorkspaceWidgetContext } from '../../../core/workspace-sdk/runtime/workspace-widget-context';

interface EnvironmentResponse {
  readonly id: string;
  readonly name: string;
}

@Component({
  selector: 'deja-workspace-client-management-widget',
  standalone: true,
  imports: [ClientManagementComponent],
  template: `
    @if (loadingEnvironments()) {
      <div class="scope-state">Carregando ambientes...</div>
    } @else if (environmentError()) {
      <div class="scope-state scope-state--error">
        <p>{{ environmentError() }}</p>

        <button type="button" (click)="loadEnvironments()">Tentar novamente</button>
      </div>
    } @else if (currentUser) {
      <deja-client-management
        [service]="composition.service"
        [environments]="environments()"
        [defaultEnvironmentId]="currentUser.environmentId"
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
export class WorkspaceClientManagementWidgetComponent implements OnInit {
  private readonly http = inject(HttpClient);

  private readonly authentication = inject(AuthenticationService);

  protected readonly currentUser = this.authentication.user();

  protected readonly composition = new ClientsComposition(this.http);

  protected readonly environments = signal<readonly ClientEnvironmentOption[]>([]);

  protected readonly loadingEnvironments = signal(false);

  protected readonly environmentError = signal<string | null>(null);

  protected readonly canManage = [
    'platform_admin',
    'organization_admin',
    'tenant_admin',
    'manager',
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
    if (this.canManage) {
      void this.loadEnvironments();
    }
  }

  protected async loadEnvironments(): Promise<void> {
    this.loadingEnvironments.set(true);
    this.environmentError.set(null);

    try {
      const environments = await firstValueFrom(
        this.http.get<readonly EnvironmentResponse[]>('/api/v1/environments'),
      );

      this.environments.set(
        environments.map((environment) => ({
          id: environment.id,
          name: environment.name,
        })),
      );
    } catch {
      this.environmentError.set('Não foi possível carregar os ambientes.');
    } finally {
      this.loadingEnvironments.set(false);
    }
  }
}
