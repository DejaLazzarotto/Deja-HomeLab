/*
 * Deja Workspace Angular Integration
 *
 * Workspace Dashboard Component
 *
 * Componente responsável pela representação visual institucional
 * de um Dashboard resolvido pelo Workspace Runtime.
 */

import {
  ChangeDetectionStrategy,
  Component,
  Input,
} from '@angular/core';

import {
  WorkspaceResolvedDashboard,
} from '../../../core/workspace-sdk/runtime/workspace-resolved-dashboard';

/**
 * Representação Angular de um Workspace Dashboard.
 *
 * Nesta primeira implementação, o componente apresenta somente
 * as informações institucionais básicas do Dashboard.
 *
 * Layouts e Widgets serão integrados nas próximas etapas.
 */
@Component({
  selector: 'deja-workspace-dashboard',
  standalone: true,
  template: `
    <section class="workspace-dashboard">
      <header class="workspace-dashboard__header">
        <h1 class="workspace-dashboard__title">
          {{ resolvedDashboard.dashboard.title }}
        </h1>

        @if (resolvedDashboard.dashboard.description) {
          <p class="workspace-dashboard__description">
            {{ resolvedDashboard.dashboard.description }}
          </p>
        }
      </header>
    </section>
  `,
  styles: `
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .workspace-dashboard {
      display: block;
      width: 100%;
      height: 100%;
    }

    .workspace-dashboard__header {
      display: block;
    }

    .workspace-dashboard__title {
      margin: 0;
    }

    .workspace-dashboard__description {
      margin: 0;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceDashboardComponent {

  /**
   * Dashboard completamente resolvido pelo Workspace Runtime.
   */
  @Input({
    required: true,
  })
  resolvedDashboard!: WorkspaceResolvedDashboard;

}