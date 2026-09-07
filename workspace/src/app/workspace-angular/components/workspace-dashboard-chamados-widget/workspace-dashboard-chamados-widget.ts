/*
 * Deja Workspace Angular Integration
 *
 * Dashboard Chamados Widget
 *
 * Integra o Dashboard de Chamados ao Workspace institucional.
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
  Client,
  ClientsComposition,
} from '../../../deja-chamados/clients';

import {
  DashboardData,
  DashboardManagerData,
  DashboardOverviewComponent,
  DashboardService,
  DashboardSlaData,
} from '../../../deja-chamados/dashboard';

import {
  Ticket,
  TicketTimelineEvent,
  TicketsComposition,
} from '../../../deja-chamados/tickets';

import {
  WorkspaceWidgetInstance,
} from '../../../core/workspace-sdk/runtime/workspace-widget';

import {
  WorkspaceWidgetContext,
} from '../../../core/workspace-sdk/runtime/workspace-widget-context';

@Component({
  selector: 'deja-workspace-dashboard-chamados-widget',
  standalone: true,
  imports: [
    DashboardOverviewComponent,
  ],
  template: `
    @if (loading()) {
      <div class="scope-state">
        Carregando dashboard...
      </div>
    } @else if (errorMessage()) {
      <div class="scope-state scope-state--error">
        <p>{{ errorMessage() }}</p>

        <button
          type="button"
          (click)="loadDashboard()"
        >
          Tentar novamente
        </button>
      </div>
    } @else if (
      dashboardData() &&
      slaData() &&
      managerData()
    ) {
      <deja-dashboard-overview
        [dashboardData]="dashboardData()!"
        [slaData]="slaData()!"
        [managerData]="managerData()!"
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
export class WorkspaceDashboardChamadosWidgetComponent
implements OnInit {

  private readonly http = inject(HttpClient);

  private readonly clientsComposition =
    new ClientsComposition(this.http);

  private readonly ticketsComposition =
    new TicketsComposition(this.http);

  private readonly dashboardService =
    new DashboardService();

  protected readonly loading =
    signal(false);

  protected readonly errorMessage =
    signal<string | null>(null);

  protected readonly dashboardData =
    signal<DashboardData | null>(null);

  protected readonly slaData =
    signal<DashboardSlaData | null>(null);

  protected readonly managerData =
    signal<DashboardManagerData | null>(null);

  @Input({
    required: true,
  })
  widgetInstance!: WorkspaceWidgetInstance;

  @Input({
    required: true,
  })
  widgetContext!: WorkspaceWidgetContext;

  ngOnInit(): void {
    void this.loadDashboard();
  }

  protected async loadDashboard(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set(null);

    try {
      const [
        clients,
        tickets,
      ] = await Promise.all([
        this.clientsComposition.service.list(),
        this.ticketsComposition.service.list(),
      ]);

      const timelineByTicketId =
        await this.loadTimelines(tickets);

      const source = {
        clients,
        tickets,
        timelineByTicketId,
      };

      this.dashboardData.set(
        this.dashboardService.buildDashboardData(
          source,
        ),
      );

      this.slaData.set(
        this.dashboardService.buildSlaData(
          source,
        ),
      );

      this.managerData.set(
        this.dashboardService.buildManagerData(
          source,
        ),
      );
    } catch {
      this.errorMessage.set(
        'Não foi possível carregar o dashboard de chamados.',
      );
    } finally {
      this.loading.set(false);
    }
  }

  private async loadTimelines(
    tickets: readonly Ticket[],
  ): Promise<
    ReadonlyMap<
      string,
      readonly TicketTimelineEvent[]
    >
  > {
    const entries = await Promise.all(
      tickets.map(async (ticket) => {
        const timeline =
          await this.ticketsComposition.timelineService
            .listByTicketId(ticket.id);

        return [
          ticket.id,
          timeline,
        ] as const;
      }),
    );

    return new Map(entries);
  }

}