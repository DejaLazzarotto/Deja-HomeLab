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
  WorkspaceRuntime,
} from '../../../core/workspace-sdk/runtime/workspace-runtime';

import {
  WorkspaceResolvedDashboard,
} from '../../../core/workspace-sdk/runtime/workspace-resolved-dashboard';

import {
  WorkspaceWidgetHostComponent,
} from '../workspace-widget-host/workspace-widget-host';

/**
 * Representação Angular de um Workspace Dashboard.
 */
@Component({
  selector: 'deja-workspace-dashboard',
  standalone: true,
  imports: [
    WorkspaceWidgetHostComponent,
  ],
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

      <section class="workspace-dashboard__widgets">

        @for (
          widget of resolvedDashboard.widgets;
          track widget.id
        ) {

          <deja-workspace-widget-host
            [runtime]="runtime"
            [widgetInstance]="widget" />

        }

      </section>

    </section>
  `,
  styles: `
    :host {
      display: block;
      width: 100%;
      height: 100%;
    }

    .workspace-dashboard {
      display: flex;
      flex-direction: column;
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

    .workspace-dashboard__widgets {
      display: block;
      flex: 1;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class WorkspaceDashboardComponent {

  /**
   * Runtime oficial do Workspace.
   */
  @Input({
    required: true,
  })
  runtime!: WorkspaceRuntime;

  /**
   * Dashboard completamente resolvido pelo Workspace Runtime.
   */
  @Input({
    required: true,
  })
  resolvedDashboard!: WorkspaceResolvedDashboard;

}